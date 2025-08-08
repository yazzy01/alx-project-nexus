from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Movie, Genre, FavoriteMovie, MovieRating, 
    Watchlist, UserProfile, RecommendationHistory
)


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model"""
    
    class Meta:
        model = Genre
        fields = ['id', 'tmdb_id', 'name']


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie model"""
    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.ReadOnlyField()
    backdrop_url = serializers.ReadOnlyField()
    is_favorite = serializers.SerializerMethodField()
    is_in_watchlist = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'title', 'overview', 'release_date',
            'poster_path', 'backdrop_path', 'poster_url', 'backdrop_url',
            'vote_average', 'vote_count', 'popularity', 'adult',
            'original_language', 'original_title', 'genres',
            'is_favorite', 'is_in_watchlist', 'user_rating',
            'created_at', 'updated_at'
        ]
    
    def get_is_favorite(self, obj):
        """Check if movie is in user's favorites"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoriteMovie.objects.filter(
                user=request.user, movie=obj
            ).exists()
        return False
    
    def get_is_in_watchlist(self, obj):
        """Check if movie is in user's watchlist"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Watchlist.objects.filter(
                user=request.user, movie=obj
            ).exists()
        return False
    
    def get_user_rating(self, obj):
        """Get user's rating for this movie"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = MovieRating.objects.get(user=request.user, movie=obj)
                return {
                    'rating': rating.rating,
                    'review': rating.review,
                    'created_at': rating.created_at
                }
            except MovieRating.DoesNotExist:
                return None
        return None


class MovieListSerializer(serializers.ModelSerializer):
    """Simplified serializer for movie lists"""
    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'title', 'release_date',
            'poster_path', 'poster_url', 'vote_average',
            'vote_count', 'popularity', 'genres'
        ]


class FavoriteMovieSerializer(serializers.ModelSerializer):
    """Serializer for FavoriteMovie model"""
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FavoriteMovie
        fields = ['id', 'movie', 'movie_id', 'added_at']
    
    def create(self, validated_data):
        """Create a new favorite movie entry"""
        movie_id = validated_data.pop('movie_id')
        try:
            movie = Movie.objects.get(id=movie_id)
            validated_data['movie'] = movie
            return super().create(validated_data)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found")


class MovieRatingSerializer(serializers.ModelSerializer):
    """Serializer for MovieRating model"""
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = MovieRating
        fields = [
            'id', 'movie', 'movie_id', 'user', 'rating', 
            'review', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Create a new movie rating"""
        movie_id = validated_data.pop('movie_id')
        try:
            movie = Movie.objects.get(id=movie_id)
            validated_data['movie'] = movie
            return super().create(validated_data)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found")
    
    def validate_rating(self, value):
        """Validate rating is within acceptable range"""
        if value < 0.5 or value > 5.0:
            raise serializers.ValidationError(
                "Rating must be between 0.5 and 5.0"
            )
        return value


class WatchlistSerializer(serializers.ModelSerializer):
    """Serializer for Watchlist model"""
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Watchlist
        fields = ['id', 'movie', 'movie_id', 'added_at']
    
    def create(self, validated_data):
        """Create a new watchlist entry"""
        movie_id = validated_data.pop('movie_id')
        try:
            movie = Movie.objects.get(id=movie_id)
            validated_data['movie'] = movie
            return super().create(validated_data)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found")


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = serializers.StringRelatedField(read_only=True)
    favorite_genres = GenreSerializer(many=True, read_only=True)
    favorite_movies_count = serializers.SerializerMethodField()
    watchlist_count = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'favorite_genres', 'date_joined',
            'favorite_movies_count', 'watchlist_count', 'ratings_count'
        ]
    
    def get_favorite_movies_count(self, obj):
        """Get count of user's favorite movies"""
        return obj.user.favorite_movies.count()
    
    def get_watchlist_count(self, obj):
        """Get count of movies in user's watchlist"""
        return obj.user.watchlist.count()
    
    def get_ratings_count(self, obj):
        """Get count of user's movie ratings"""
        return obj.user.movie_ratings.count()


class RecommendationHistorySerializer(serializers.ModelSerializer):
    """Serializer for RecommendationHistory model"""
    movie = MovieListSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = RecommendationHistory
        fields = [
            'id', 'user', 'movie', 'recommendation_type',
            'score', 'clicked', 'created_at'
        ]


class MovieSearchSerializer(serializers.Serializer):
    """Serializer for movie search parameters"""
    query = serializers.CharField(max_length=255, required=True)
    page = serializers.IntegerField(default=1, min_value=1)
    include_adult = serializers.BooleanField(default=False)
    year = serializers.IntegerField(required=False, min_value=1900)
    
    def validate_query(self, value):
        """Validate search query"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Search query must be at least 2 characters long"
            )
        return value.strip()


class RecommendationRequestSerializer(serializers.Serializer):
    """Serializer for recommendation request parameters"""
    recommendation_type = serializers.ChoiceField(
        choices=[
            ('trending', 'Trending'),
            ('popular', 'Popular'),
            ('genre_based', 'Genre Based'),
            ('similar', 'Similar Movies'),
        ],
        default='popular'
    )
    genre_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    page = serializers.IntegerField(default=1, min_value=1)
    limit = serializers.IntegerField(default=20, min_value=1, max_value=100)