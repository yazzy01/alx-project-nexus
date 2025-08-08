from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .models import (
    Movie, Genre, FavoriteMovie, MovieRating, 
    Watchlist, UserProfile, RecommendationHistory
)
from .serializers import (
    MovieSerializer, MovieListSerializer, GenreSerializer,
    FavoriteMovieSerializer, MovieRatingSerializer, WatchlistSerializer,
    UserProfileSerializer, MovieSearchSerializer, RecommendationRequestSerializer
)
from .services import tmdb_service, recommendation_service
from users.models import UserActivity

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for movie results"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MovieListView(generics.ListAPIView):
    """List all movies with filtering and search capabilities"""
    serializer_class = MovieListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Movie.objects.all()
        
        # Filter by genre
        genre_ids = self.request.query_params.getlist('genre')
        if genre_ids:
            queryset = queryset.filter(genres__tmdb_id__in=genre_ids).distinct()
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(release_date__year=year)
        
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            try:
                queryset = queryset.filter(vote_average__gte=float(min_rating))
            except ValueError:
                pass
        
        # Search by title
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(overview__icontains=search)
            )
        
        # Sort options
        sort_by = self.request.query_params.get('sort_by', 'popularity')
        if sort_by == 'rating':
            queryset = queryset.order_by('-vote_average', '-vote_count')
        elif sort_by == 'release_date':
            queryset = queryset.order_by('-release_date')
        elif sort_by == 'title':
            queryset = queryset.order_by('title')
        else:  # default to popularity
            queryset = queryset.order_by('-popularity')
        
        return queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('genre', openapi.IN_QUERY, description="Filter by genre ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('year', openapi.IN_QUERY, description="Filter by release year", type=openapi.TYPE_INTEGER),
            openapi.Parameter('min_rating', openapi.IN_QUERY, description="Minimum rating", type=openapi.TYPE_NUMBER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in title and overview", type=openapi.TYPE_STRING),
            openapi.Parameter('sort_by', openapi.IN_QUERY, description="Sort by: popularity, rating, release_date, title", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MovieDetailView(generics.RetrieveAPIView):
    """Get detailed information about a specific movie"""
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'tmdb_id'
    
    def get_queryset(self):
        return Movie.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Log user activity if authenticated
        if request.user.is_authenticated:
            UserActivity.objects.create(
                user=request.user,
                activity_type='view_movie',
                movie_id=instance.tmdb_id,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class GenreListView(generics.ListAPIView):
    """List all available movie genres"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('type', openapi.IN_QUERY, description="Recommendation type: trending, popular, top_rated, upcoming", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
    ],
    responses={200: MovieListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_recommendations(request):
    """Get movie recommendations from TMDb"""
    recommendation_type = request.query_params.get('type', 'popular')
    page = int(request.query_params.get('page', 1))
    
    try:
        if recommendation_type == 'trending':
            movies = recommendation_service.get_trending_recommendations(
                user=request.user if request.user.is_authenticated else None,
                page=page
            )
        elif recommendation_type == 'top_rated':
            # Get top rated movies from TMDb
            top_rated_data = tmdb_service.get_top_rated_movies(page=page)
            if top_rated_data and 'results' in top_rated_data:
                movies = tmdb_service.sync_movies_to_db(top_rated_data['results'])
            else:
                movies = []
        elif recommendation_type == 'upcoming':
            # Get upcoming movies from TMDb
            upcoming_data = tmdb_service.get_upcoming_movies(page=page)
            if upcoming_data and 'results' in upcoming_data:
                movies = tmdb_service.sync_movies_to_db(upcoming_data['results'])
            else:
                movies = []
        else:  # default to popular
            movies = recommendation_service.get_popular_recommendations(
                user=request.user if request.user.is_authenticated else None,
                page=page
            )
        
        serializer = MovieListSerializer(movies, many=True, context={'request': request})
        return Response(serializer.data)
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return Response(
            {'error': 'Failed to fetch recommendations'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    request_body=MovieSearchSerializer,
    responses={200: MovieListSerializer(many=True)}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def search_movies(request):
    """Search for movies using TMDb API"""
    serializer = MovieSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    query = serializer.validated_data['query']
    page = serializer.validated_data.get('page', 1)
    include_adult = serializer.validated_data.get('include_adult', False)
    year = serializer.validated_data.get('year')
    
    try:
        # Search movies using TMDb API
        search_data = tmdb_service.search_movies(
            query=query,
            page=page,
            include_adult=include_adult,
            year=year
        )
        
        if not search_data or 'results' not in search_data:
            return Response({'results': []})
        
        # Sync movies to database
        movies = tmdb_service.sync_movies_to_db(search_data['results'])
        
        # Log search activity
        if request.user.is_authenticated:
            UserActivity.objects.create(
                user=request.user,
                activity_type='search',
                metadata={'query': query, 'results_count': len(movies)},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        serializer = MovieListSerializer(movies, many=True, context={'request': request})
        return Response({
            'results': serializer.data,
            'total_results': search_data.get('total_results', 0),
            'total_pages': search_data.get('total_pages', 1),
            'page': page
        })
    
    except Exception as e:
        logger.error(f"Error searching movies: {e}")
        return Response(
            {'error': 'Failed to search movies'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class FavoriteMovieListView(generics.ListCreateAPIView):
    """List and add favorite movies for authenticated user"""
    serializer_class = FavoriteMovieSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return FavoriteMovie.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='add_favorite',
            movie_id=serializer.instance.movie.tmdb_id,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class FavoriteMovieDetailView(generics.DestroyAPIView):
    """Remove a movie from favorites"""
    serializer_class = FavoriteMovieSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FavoriteMovie.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='remove_favorite',
            movie_id=instance.movie.tmdb_id,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        instance.delete()


class MovieRatingListView(generics.ListCreateAPIView):
    """List and create movie ratings for authenticated user"""
    serializer_class = MovieRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return MovieRating.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='rate_movie',
            movie_id=serializer.instance.movie.tmdb_id,
            metadata={'rating': serializer.instance.rating},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class MovieRatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a movie rating"""
    serializer_class = MovieRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MovieRating.objects.filter(user=self.request.user)


class WatchlistListView(generics.ListCreateAPIView):
    """List and add movies to watchlist for authenticated user"""
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='add_watchlist',
            movie_id=serializer.instance.movie.tmdb_id,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class WatchlistDetailView(generics.DestroyAPIView):
    """Remove a movie from watchlist"""
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='remove_watchlist',
            movie_id=instance.movie.tmdb_id,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        instance.delete()


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('movie_id', openapi.IN_QUERY, description="TMDb movie ID for similar movies", type=openapi.TYPE_INTEGER),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
    ],
    responses={200: MovieListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_similar_movies(request):
    """Get movies similar to a specific movie"""
    movie_id = request.query_params.get('movie_id')
    page = int(request.query_params.get('page', 1))
    
    if not movie_id:
        return Response(
            {'error': 'movie_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        movie_id = int(movie_id)
        movies = recommendation_service.get_similar_movie_recommendations(
            movie_id=movie_id,
            user=request.user if request.user.is_authenticated else None,
            page=page
        )
        
        serializer = MovieListSerializer(movies, many=True, context={'request': request})
        return Response(serializer.data)
    
    except ValueError:
        return Response(
            {'error': 'Invalid movie_id'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error getting similar movies: {e}")
        return Response(
            {'error': 'Failed to fetch similar movies'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def sync_genres(request):
    """Sync genres from TMDb API to local database (Admin only)"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        success = tmdb_service.sync_genres_to_db()
        if success:
            return Response({'message': 'Genres synced successfully'})
        else:
            return Response(
                {'error': 'Failed to sync genres'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        logger.error(f"Error syncing genres: {e}")
        return Response(
            {'error': 'Failed to sync genres'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )