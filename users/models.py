from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserActivity(models.Model):
    """Model to track user activity for analytics and recommendations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(
        max_length=50,
        choices=[
            ('login', 'Login'),
            ('logout', 'Logout'),
            ('view_movie', 'View Movie'),
            ('rate_movie', 'Rate Movie'),
            ('add_favorite', 'Add to Favorites'),
            ('remove_favorite', 'Remove from Favorites'),
            ('add_watchlist', 'Add to Watchlist'),
            ('remove_watchlist', 'Remove from Watchlist'),
            ('search', 'Search'),
            ('view_recommendations', 'View Recommendations'),
        ]
    )
    movie_id = models.IntegerField(null=True, blank=True)  # TMDb movie ID
    metadata = models.JSONField(default=dict, blank=True)  # Additional activity data
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['movie_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"


class UserPreferences(models.Model):
    """Model for storing user preferences and settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    recommendation_emails = models.BooleanField(default=True)
    
    # Content preferences
    include_adult_content = models.BooleanField(default=False)
    preferred_language = models.CharField(max_length=10, default='en')
    
    # Recommendation preferences
    enable_collaborative_filtering = models.BooleanField(default=True)
    enable_content_based_filtering = models.BooleanField(default=True)
    recommendation_diversity = models.FloatField(default=0.5)  # 0.0 to 1.0
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('friends', 'Friends Only'),
            ('private', 'Private'),
        ],
        default='public'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create user preferences when a new user is created"""
    if created:
        UserPreferences.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_preferences(sender, instance, **kwargs):
    """Save user preferences when user is saved"""
    if hasattr(instance, 'preferences'):
        instance.preferences.save()
    else:
        UserPreferences.objects.create(user=instance)