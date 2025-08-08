from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    """Model for movie genres"""
    tmdb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Movie(models.Model):
    """Model for movies from TMDb API"""
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, blank=True)
    backdrop_path = models.CharField(max_length=255, blank=True)
    vote_average = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        default=0.0
    )
    vote_count = models.IntegerField(default=0)
    popularity = models.FloatField(default=0.0)
    adult = models.BooleanField(default=False)
    original_language = models.CharField(max_length=10, blank=True)
    original_title = models.CharField(max_length=255, blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-popularity', '-vote_average']
        indexes = [
            models.Index(fields=['tmdb_id']),
            models.Index(fields=['release_date']),
            models.Index(fields=['vote_average']),
            models.Index(fields=['popularity']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'Unknown'})"
    
    @property
    def poster_url(self):
        """Return full poster URL"""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None
    
    @property
    def backdrop_url(self):
        """Return full backdrop URL"""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{self.backdrop_path}"
        return None


class UserProfile(models.Model):
    """Extended user profile for movie preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favorite_genres = models.ManyToManyField(Genre, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class FavoriteMovie(models.Model):
    """Model for user's favorite movies"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"


class MovieRating(models.Model):
    """Model for user movie ratings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_ratings')
    rating = models.FloatField(
        validators=[MinValueValidator(0.5), MaxValueValidator(5.0)]
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.rating}/5"


class Watchlist(models.Model):
    """Model for user's watchlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='in_watchlists')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username}'s Watchlist - {self.movie.title}"


class RecommendationHistory(models.Model):
    """Model to track recommendation history for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendation_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    recommendation_type = models.CharField(
        max_length=50,
        choices=[
            ('trending', 'Trending'),
            ('popular', 'Popular'),
            ('genre_based', 'Genre Based'),
            ('collaborative', 'Collaborative Filtering'),
            ('content_based', 'Content Based'),
        ]
    )
    score = models.FloatField(default=0.0)  # Recommendation confidence score
    clicked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'recommendation_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.recommendation_type})"