from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

from .services import tmdb_service
from .models import Movie, Genre

logger = logging.getLogger(__name__)


@shared_task
def sync_trending_movies():
    """Background task to sync trending movies from TMDb"""
    try:
        logger.info("Starting sync of trending movies")
        
        # Get trending movies for the week
        trending_data = tmdb_service.get_trending_movies(time_window='week')
        if trending_data and 'results' in trending_data:
            movies = tmdb_service.sync_movies_to_db(trending_data['results'])
            logger.info(f"Successfully synced {len(movies)} trending movies")
            return f"Synced {len(movies)} trending movies"
        else:
            logger.error("Failed to fetch trending movies from TMDb")
            return "Failed to fetch trending movies"
    
    except Exception as e:
        logger.error(f"Error syncing trending movies: {e}")
        return f"Error: {str(e)}"


@shared_task
def sync_popular_movies():
    """Background task to sync popular movies from TMDb"""
    try:
        logger.info("Starting sync of popular movies")
        
        # Get multiple pages of popular movies
        all_movies = []
        for page in range(1, 6):  # Get first 5 pages
            popular_data = tmdb_service.get_popular_movies(page=page)
            if popular_data and 'results' in popular_data:
                movies = tmdb_service.sync_movies_to_db(popular_data['results'])
                all_movies.extend(movies)
            else:
                break
        
        logger.info(f"Successfully synced {len(all_movies)} popular movies")
        return f"Synced {len(all_movies)} popular movies"
    
    except Exception as e:
        logger.error(f"Error syncing popular movies: {e}")
        return f"Error: {str(e)}"


@shared_task
def sync_top_rated_movies():
    """Background task to sync top rated movies from TMDb"""
    try:
        logger.info("Starting sync of top rated movies")
        
        # Get multiple pages of top rated movies
        all_movies = []
        for page in range(1, 6):  # Get first 5 pages
            top_rated_data = tmdb_service.get_top_rated_movies(page=page)
            if top_rated_data and 'results' in top_rated_data:
                movies = tmdb_service.sync_movies_to_db(top_rated_data['results'])
                all_movies.extend(movies)
            else:
                break
        
        logger.info(f"Successfully synced {len(all_movies)} top rated movies")
        return f"Synced {len(all_movies)} top rated movies"
    
    except Exception as e:
        logger.error(f"Error syncing top rated movies: {e}")
        return f"Error: {str(e)}"


@shared_task
def sync_upcoming_movies():
    """Background task to sync upcoming movies from TMDb"""
    try:
        logger.info("Starting sync of upcoming movies")
        
        # Get multiple pages of upcoming movies
        all_movies = []
        for page in range(1, 4):  # Get first 3 pages
            upcoming_data = tmdb_service.get_upcoming_movies(page=page)
            if upcoming_data and 'results' in upcoming_data:
                movies = tmdb_service.sync_movies_to_db(upcoming_data['results'])
                all_movies.extend(movies)
            else:
                break
        
        logger.info(f"Successfully synced {len(all_movies)} upcoming movies")
        return f"Synced {len(all_movies)} upcoming movies"
    
    except Exception as e:
        logger.error(f"Error syncing upcoming movies: {e}")
        return f"Error: {str(e)}"


@shared_task
def sync_genres():
    """Background task to sync genres from TMDb"""
    try:
        logger.info("Starting sync of genres")
        
        success = tmdb_service.sync_genres_to_db()
        if success:
            logger.info("Successfully synced genres")
            return "Genres synced successfully"
        else:
            logger.error("Failed to sync genres")
            return "Failed to sync genres"
    
    except Exception as e:
        logger.error(f"Error syncing genres: {e}")
        return f"Error: {str(e)}"


@shared_task
def update_movie_details(movie_tmdb_id):
    """Background task to update detailed movie information"""
    try:
        logger.info(f"Updating details for movie {movie_tmdb_id}")
        
        # Get detailed movie information
        movie_data = tmdb_service.get_movie_details(movie_tmdb_id)
        if movie_data:
            movie = tmdb_service.sync_movie_to_db(movie_data)
            if movie:
                logger.info(f"Successfully updated movie {movie.title}")
                return f"Updated movie: {movie.title}"
            else:
                logger.error(f"Failed to sync movie {movie_tmdb_id}")
                return f"Failed to sync movie {movie_tmdb_id}"
        else:
            logger.error(f"Failed to fetch details for movie {movie_tmdb_id}")
            return f"Failed to fetch details for movie {movie_tmdb_id}"
    
    except Exception as e:
        logger.error(f"Error updating movie details: {e}")
        return f"Error: {str(e)}"


@shared_task
def cleanup_old_cache():
    """Background task to cleanup old cache entries"""
    try:
        logger.info("Starting cache cleanup")
        
        # This is a placeholder for cache cleanup logic
        # In a real implementation, you might want to:
        # 1. Remove expired cache entries
        # 2. Clean up old recommendation history
        # 3. Remove old user activities
        
        # Clean up old recommendation history (older than 30 days)
        from .models import RecommendationHistory
        cutoff_date = timezone.now() - timedelta(days=30)
        old_recommendations = RecommendationHistory.objects.filter(
            created_at__lt=cutoff_date
        )
        count = old_recommendations.count()
        old_recommendations.delete()
        
        logger.info(f"Cleaned up {count} old recommendation entries")
        return f"Cleaned up {count} old recommendation entries"
    
    except Exception as e:
        logger.error(f"Error during cache cleanup: {e}")
        return f"Error: {str(e)}"


@shared_task
def generate_user_recommendations(user_id):
    """Background task to generate personalized recommendations for a user"""
    try:
        from django.contrib.auth.models import User
        from .services import recommendation_service
        
        logger.info(f"Generating recommendations for user {user_id}")
        
        user = User.objects.get(id=user_id)
        
        # Generate different types of recommendations
        trending_movies = recommendation_service.get_trending_recommendations(user=user)
        popular_movies = recommendation_service.get_popular_recommendations(user=user)
        
        # If user has favorite genres, generate genre-based recommendations
        if hasattr(user, 'profile') and user.profile.favorite_genres.exists():
            genre_ids = list(user.profile.favorite_genres.values_list('tmdb_id', flat=True))
            genre_movies = recommendation_service.get_genre_based_recommendations(
                user=user, 
                genre_ids=genre_ids
            )
        else:
            genre_movies = []
        
        total_recommendations = len(trending_movies) + len(popular_movies) + len(genre_movies)
        
        logger.info(f"Generated {total_recommendations} recommendations for user {user.username}")
        return f"Generated {total_recommendations} recommendations for user {user.username}"
    
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {e}")
        return f"Error: {str(e)}"


@shared_task
def daily_data_sync():
    """Daily task to sync all movie data"""
    try:
        logger.info("Starting daily data sync")
        
        results = []
        
        # Sync genres first
        genre_result = sync_genres.delay()
        results.append(f"Genres: {genre_result.get()}")
        
        # Sync different movie categories
        trending_result = sync_trending_movies.delay()
        results.append(f"Trending: {trending_result.get()}")
        
        popular_result = sync_popular_movies.delay()
        results.append(f"Popular: {popular_result.get()}")
        
        top_rated_result = sync_top_rated_movies.delay()
        results.append(f"Top Rated: {top_rated_result.get()}")
        
        upcoming_result = sync_upcoming_movies.delay()
        results.append(f"Upcoming: {upcoming_result.get()}")
        
        # Cleanup old data
        cleanup_result = cleanup_old_cache.delay()
        results.append(f"Cleanup: {cleanup_result.get()}")
        
        logger.info("Daily data sync completed")
        return "Daily sync completed: " + "; ".join(results)
    
    except Exception as e:
        logger.error(f"Error during daily data sync: {e}")
        return f"Error: {str(e)}"