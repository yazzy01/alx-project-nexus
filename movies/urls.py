from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    # Movie endpoints
    path('', views.MovieListView.as_view(), name='movie-list'),
    path('<int:tmdb_id>/', views.MovieDetailView.as_view(), name='movie-detail'),
    
    # Genre endpoints
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    
    # Recommendation endpoints
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('similar/', views.get_similar_movies, name='similar-movies'),
    
    # Search endpoints
    path('search/', views.search_movies, name='search-movies'),
    
    # User-specific movie endpoints
    path('favorites/', views.FavoriteMovieListView.as_view(), name='favorite-list'),
    path('favorites/<int:pk>/', views.FavoriteMovieDetailView.as_view(), name='favorite-detail'),
    
    path('ratings/', views.MovieRatingListView.as_view(), name='rating-list'),
    path('ratings/<int:pk>/', views.MovieRatingDetailView.as_view(), name='rating-detail'),
    
    path('watchlist/', views.WatchlistListView.as_view(), name='watchlist-list'),
    path('watchlist/<int:pk>/', views.WatchlistDetailView.as_view(), name='watchlist-detail'),
    
    # Admin endpoints
    path('sync-genres/', views.sync_genres, name='sync-genres'),
]