from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Movie, Genre, FavoriteMovie, MovieRating, 
    Watchlist, UserProfile, RecommendationHistory
)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'tmdb_id']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'release_date', 'vote_average', 
        'vote_count', 'popularity', 'get_genres'
    ]
    list_filter = [
        'release_date', 'adult', 'original_language', 
        'genres', 'vote_average'
    ]
    search_fields = ['title', 'overview', 'original_title']
    readonly_fields = ['tmdb_id', 'created_at', 'updated_at', 'poster_image', 'backdrop_image']
    filter_horizontal = ['genres']
    date_hierarchy = 'release_date'
    ordering = ['-popularity', '-vote_average']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tmdb_id', 'title', 'original_title', 'overview')
        }),
        ('Release Information', {
            'fields': ('release_date', 'original_language', 'adult')
        }),
        ('Ratings & Popularity', {
            'fields': ('vote_average', 'vote_count', 'popularity')
        }),
        ('Images', {
            'fields': ('poster_path', 'poster_image', 'backdrop_path', 'backdrop_image'),
            'classes': ('collapse',)
        }),
        ('Categorization', {
            'fields': ('genres',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_genres(self, obj):
        """Display genres as comma-separated list"""
        return ", ".join([genre.name for genre in obj.genres.all()])
    get_genres.short_description = 'Genres'
    
    def poster_image(self, obj):
        """Display poster image in admin"""
        if obj.poster_url:
            return format_html(
                '<img src="{}" width="100" height="150" />',
                obj.poster_url
            )
        return "No poster"
    poster_image.short_description = 'Poster'
    
    def backdrop_image(self, obj):
        """Display backdrop image in admin"""
        if obj.backdrop_url:
            return format_html(
                '<img src="{}" width="200" height="113" />',
                obj.backdrop_url
            )
        return "No backdrop"
    backdrop_image.short_description = 'Backdrop'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_joined', 'get_favorite_genres_count']
    search_fields = ['user__username', 'user__email']
    filter_horizontal = ['favorite_genres']
    readonly_fields = ['date_joined']
    
    def get_favorite_genres_count(self, obj):
        """Get count of favorite genres"""
        return obj.favorite_genres.count()
    get_favorite_genres_count.short_description = 'Favorite Genres Count'


@admin.register(FavoriteMovie)
class FavoriteMovieAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'added_at']
    list_filter = ['added_at', 'movie__genres']
    search_fields = ['user__username', 'movie__title']
    readonly_fields = ['added_at']
    date_hierarchy = 'added_at'
    ordering = ['-added_at']


@admin.register(MovieRating)
class MovieRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'created_at', 'updated_at']
    list_filter = ['rating', 'created_at', 'movie__genres']
    search_fields = ['user__username', 'movie__title', 'review']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Rating Information', {
            'fields': ('user', 'movie', 'rating')
        }),
        ('Review', {
            'fields': ('review',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'added_at']
    list_filter = ['added_at', 'movie__genres']
    search_fields = ['user__username', 'movie__title']
    readonly_fields = ['added_at']
    date_hierarchy = 'added_at'
    ordering = ['-added_at']


@admin.register(RecommendationHistory)
class RecommendationHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'movie', 'recommendation_type', 
        'score', 'clicked', 'created_at'
    ]
    list_filter = [
        'recommendation_type', 'clicked', 'created_at', 
        'movie__genres'
    ]
    search_fields = ['user__username', 'movie__title']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Recommendation Details', {
            'fields': ('user', 'movie', 'recommendation_type', 'score')
        }),
        ('User Interaction', {
            'fields': ('clicked',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# Customize admin site headers
admin.site.site_header = "Movie Recommendation Admin"
admin.site.site_title = "Movie Recommendation Admin Portal"
admin.site.index_title = "Welcome to Movie Recommendation Administration"