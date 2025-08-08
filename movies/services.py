import requests
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from .models import Movie, Genre

logger = logging.getLogger(__name__)


class TMDbAPIService:
    """Service class for interacting with The Movie Database (TMDb) API"""
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.session = requests.Session()
        self.session.params = {'api_key': self.api_key}
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to TMDb API with error handling"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request failed: {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to parse TMDb API response: {e}")
            return None
    
    def get_trending_movies(self, time_window: str = 'week', page: int = 1) -> Optional[Dict]:
        """Get trending movies from TMDb"""
        cache_key = f"trending_movies_{time_window}_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = f"trending/movie/{time_window}"
        params = {'page': page}
        data = self._make_request(endpoint, params)
        
        if data:
            # Cache for 1 hour
            cache.set(cache_key, data, 3600)
        
        return data
    
    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """Get popular movies from TMDb"""
        cache_key = f"popular_movies_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = "movie/popular"
        params = {'page': page}
        data = self._make_request(endpoint, params)
        
        if data:
            # Cache for 2 hours
            cache.set(cache_key, data, 7200)
        
        return data
    
    def get_top_rated_movies(self, page: int = 1) -> Optional[Dict]:
        """Get top rated movies from TMDb"""
        cache_key = f"top_rated_movies_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = "movie/top_rated"
        params = {'page': page}
        data = self._make_request(endpoint, params)
        
        if data:
            # Cache for 4 hours
            cache.set(cache_key, data, 14400)
        
        return data
    
    def get_upcoming_movies(self, page: int = 1) -> Optional[Dict]:
        """Get upcoming movies from TMDb"""
        cache_key = f"upcoming_movies_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = "movie/upcoming"
        params = {'page': page}
        data = self._make_request(endpoint, params)
        
        if data:
            # Cache for 6 hours
            cache.set(cache_key, data, 21600)
        
        return data
    
    def search_movies(self, query: str, page: int = 1, include_adult: bool = False, 
                     year: Optional[int] = None) -> Optional[Dict]:
        """Search for movies on TMDb"""
        cache_key = f"search_movies_{query}_{page}_{include_adult}_{year}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = "search/movie"
        params = {
            'query': query,
            'page': page,
            'include_adult': include_adult
        }
        
        if year:
            params['year'] = year
        
        data = self._make_request(endpoint, params)
        
        if data:
            # Cache search results for 30 minutes
            cache.set(cache_key, data, 1800)
        
        return data
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed information about a specific movie"""
        cache_key = f"movie_details_{movie_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = f"movie/{movie_id}"
        params = {'append_to_response': 'credits,videos,similar,recommendations'}
        data = self._make_request(endpoint, params)
        
        if data:
            # Cache movie details for 24 hours
            cache.set(cache_key, data, 86400)
        
        return data
    
    def get_similar_movies(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """Get movies similar to a specific movie"""
        cache_key = f"similar_movies_{movie_id}_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = f"movie/{movie_id}/similar"
        params = {'page': page}
        data = self._make_request(endpoint, params)
        
        if data:
            # Cache for 4 hours
            cache.set(cache_key, data, 14400)
        
        return data
    
    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """Get movie recommendations based on a specific movie"""
        cache_key = f"movie_recommendations_{movie_id}_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = f"movie/{movie_id}/recommendations"
        params = {'page': page}
        data = self._make_request(endpoint, params)
        
        if data:
            # Cache for 4 hours
            cache.set(cache_key, data, 14400)
        
        return data
    
    def discover_movies(self, **kwargs) -> Optional[Dict]:
        """Discover movies with various filters"""
        # Create cache key from parameters
        cache_params = sorted(kwargs.items())
        cache_key = f"discover_movies_{'_'.join([f'{k}_{v}' for k, v in cache_params])}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = "discover/movie"
        data = self._make_request(endpoint, kwargs)
        
        if data:
            # Cache for 2 hours
            cache.set(cache_key, data, 7200)
        
        return data
    
    def get_genres(self) -> Optional[Dict]:
        """Get list of movie genres"""
        cache_key = "movie_genres"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = "genre/movie/list"
        data = self._make_request(endpoint)
        
        if data:
            # Cache genres for 24 hours
            cache.set(cache_key, data, 86400)
        
        return data
    
    def sync_genres_to_db(self) -> bool:
        """Sync genres from TMDb to local database"""
        try:
            genres_data = self.get_genres()
            if not genres_data or 'genres' not in genres_data:
                logger.error("Failed to fetch genres from TMDb")
                return False
            
            for genre_data in genres_data['genres']:
                Genre.objects.get_or_create(
                    tmdb_id=genre_data['id'],
                    defaults={'name': genre_data['name']}
                )
            
            logger.info(f"Successfully synced {len(genres_data['genres'])} genres")
            return True
        
        except Exception as e:
            logger.error(f"Failed to sync genres: {e}")
            return False
    
    def sync_movie_to_db(self, movie_data: Dict) -> Optional[Movie]:
        """Sync a single movie from TMDb data to local database"""
        try:
            # Extract movie data
            movie_defaults = {
                'title': movie_data.get('title', ''),
                'overview': movie_data.get('overview', ''),
                'poster_path': movie_data.get('poster_path', ''),
                'backdrop_path': movie_data.get('backdrop_path', ''),
                'vote_average': movie_data.get('vote_average', 0.0),
                'vote_count': movie_data.get('vote_count', 0),
                'popularity': movie_data.get('popularity', 0.0),
                'adult': movie_data.get('adult', False),
                'original_language': movie_data.get('original_language', ''),
                'original_title': movie_data.get('original_title', ''),
            }
            
            # Handle release date
            release_date = movie_data.get('release_date')
            if release_date:
                try:
                    from datetime import datetime
                    movie_defaults['release_date'] = datetime.strptime(
                        release_date, '%Y-%m-%d'
                    ).date()
                except ValueError:
                    movie_defaults['release_date'] = None
            
            # Create or update movie
            movie, created = Movie.objects.get_or_create(
                tmdb_id=movie_data['id'],
                defaults=movie_defaults
            )
            
            # Update existing movie if not created
            if not created:
                for key, value in movie_defaults.items():
                    setattr(movie, key, value)
                movie.save()
            
            # Sync genres
            if 'genre_ids' in movie_data:
                genre_objects = Genre.objects.filter(
                    tmdb_id__in=movie_data['genre_ids']
                )
                movie.genres.set(genre_objects)
            elif 'genres' in movie_data:
                genre_objects = []
                for genre_data in movie_data['genres']:
                    genre, _ = Genre.objects.get_or_create(
                        tmdb_id=genre_data['id'],
                        defaults={'name': genre_data['name']}
                    )
                    genre_objects.append(genre)
                movie.genres.set(genre_objects)
            
            return movie
        
        except Exception as e:
            logger.error(f"Failed to sync movie {movie_data.get('id')}: {e}")
            return None
    
    def sync_movies_to_db(self, movies_data: List[Dict]) -> List[Movie]:
        """Sync multiple movies to local database"""
        synced_movies = []
        for movie_data in movies_data:
            movie = self.sync_movie_to_db(movie_data)
            if movie:
                synced_movies.append(movie)
        
        logger.info(f"Successfully synced {len(synced_movies)} movies to database")
        return synced_movies


class RecommendationService:
    """Service for generating movie recommendations"""
    
    def __init__(self):
        self.tmdb_service = TMDbAPIService()
    
    def get_trending_recommendations(self, user=None, page: int = 1) -> List[Movie]:
        """Get trending movie recommendations"""
        trending_data = self.tmdb_service.get_trending_movies(page=page)
        if not trending_data or 'results' not in trending_data:
            return []
        
        # Sync movies to database
        movies = self.tmdb_service.sync_movies_to_db(trending_data['results'])
        
        # Log recommendation history if user is provided
        if user and user.is_authenticated:
            self._log_recommendations(user, movies, 'trending')
        
        return movies
    
    def get_popular_recommendations(self, user=None, page: int = 1) -> List[Movie]:
        """Get popular movie recommendations"""
        popular_data = self.tmdb_service.get_popular_movies(page=page)
        if not popular_data or 'results' not in popular_data:
            return []
        
        movies = self.tmdb_service.sync_movies_to_db(popular_data['results'])
        
        if user and user.is_authenticated:
            self._log_recommendations(user, movies, 'popular')
        
        return movies
    
    def get_genre_based_recommendations(self, user, genre_ids: List[int], 
                                      page: int = 1) -> List[Movie]:
        """Get recommendations based on specific genres"""
        discover_params = {
            'with_genres': ','.join(map(str, genre_ids)),
            'sort_by': 'popularity.desc',
            'page': page
        }
        
        discover_data = self.tmdb_service.discover_movies(**discover_params)
        if not discover_data or 'results' not in discover_data:
            return []
        
        movies = self.tmdb_service.sync_movies_to_db(discover_data['results'])
        
        if user and user.is_authenticated:
            self._log_recommendations(user, movies, 'genre_based')
        
        return movies
    
    def get_similar_movie_recommendations(self, movie_id: int, user=None, 
                                        page: int = 1) -> List[Movie]:
        """Get recommendations similar to a specific movie"""
        similar_data = self.tmdb_service.get_similar_movies(movie_id, page=page)
        if not similar_data or 'results' not in similar_data:
            return []
        
        movies = self.tmdb_service.sync_movies_to_db(similar_data['results'])
        
        if user and user.is_authenticated:
            self._log_recommendations(user, movies, 'content_based')
        
        return movies
    
    def _log_recommendations(self, user, movies: List[Movie], 
                           recommendation_type: str):
        """Log recommendation history for analytics"""
        from .models import RecommendationHistory
        
        try:
            for movie in movies:
                RecommendationHistory.objects.get_or_create(
                    user=user,
                    movie=movie,
                    recommendation_type=recommendation_type,
                    defaults={'score': 1.0}
                )
        except Exception as e:
            logger.error(f"Failed to log recommendations: {e}")


# Initialize services
tmdb_service = TMDbAPIService()
recommendation_service = RecommendationService()