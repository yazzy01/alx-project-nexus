from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    path('delete-account/', views.delete_account, name='delete-account'),
    
    # User preferences
    path('preferences/', views.UserPreferencesView.as_view(), name='preferences'),
    
    # User activity and stats
    path('activities/', views.UserActivityListView.as_view(), name='activities'),
    path('stats/', views.user_stats_view, name='stats'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    
    # Recommendation history
    path('recommendations-history/', views.user_recommendations_history, name='recommendations-history'),
    path('mark-recommendation-clicked/', views.mark_recommendation_clicked, name='mark-recommendation-clicked'),
]