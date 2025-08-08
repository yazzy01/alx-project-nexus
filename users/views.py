from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .models import UserActivity, UserPreferences
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileUpdateSerializer, PasswordChangeSerializer,
    UserPreferencesSerializer, UserActivitySerializer, UserStatsSerializer
)

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        # Log registration activity
        UserActivity.objects.create(
            user=user,
            activity_type='register',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            description="Login successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Create or get authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        # Log login activity
        UserActivity.objects.create(
            user=user,
            activity_type='login',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """User logout endpoint"""
    try:
        # Log logout activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='logout',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Delete the user's token
        request.user.auth_token.delete()
        
        return Response({'message': 'Logout successful'})
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return Response(
            {'error': 'Logout failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get(self, request, *args, **kwargs):
        """Get user profile with additional information"""
        user = self.get_object()
        user_data = UserSerializer(user).data
        
        # Add additional profile information
        profile_data = {
            'user': user_data,
            'preferences': UserPreferencesSerializer(user.preferences).data,
            'stats': self._get_user_stats(user)
        }
        
        return Response(profile_data)
    
    def _get_user_stats(self, user):
        """Get user statistics"""
        return {
            'total_favorites': user.favorite_movies.count(),
            'total_watchlist': user.watchlist.count(),
            'total_ratings': user.movie_ratings.count(),
            'total_activities': user.activities.count(),
        }


class PasswordChangeView(generics.GenericAPIView):
    """Change user password"""
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            # Log password change activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='password_change',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """Get and update user preferences"""
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preferences, created = UserPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences


class UserActivityListView(generics.ListAPIView):
    """List user activities"""
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)[:50]  # Last 50 activities


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats_view(request):
    """Get detailed user statistics"""
    user = request.user
    serializer = UserStatsSerializer(user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """Get user dashboard data"""
    user = request.user
    
    try:
        # Get recent activities
        recent_activities = UserActivity.objects.filter(user=user)[:10]
        
        # Get favorite movies count by genre
        favorite_genres = {}
        for favorite in user.favorite_movies.all():
            for genre in favorite.movie.genres.all():
                favorite_genres[genre.name] = favorite_genres.get(genre.name, 0) + 1
        
        # Get recent ratings
        recent_ratings = user.movie_ratings.all()[:5]
        
        # Calculate average rating
        avg_rating = 0.0
        if recent_ratings:
            total_rating = sum(rating.rating for rating in user.movie_ratings.all())
            avg_rating = total_rating / user.movie_ratings.count()
        
        dashboard_data = {
            'user': UserSerializer(user).data,
            'stats': {
                'total_favorites': user.favorite_movies.count(),
                'total_watchlist': user.watchlist.count(),
                'total_ratings': user.movie_ratings.count(),
                'average_rating': round(avg_rating, 2),
                'total_activities': user.activities.count(),
            },
            'recent_activities': UserActivitySerializer(recent_activities, many=True).data,
            'favorite_genres': dict(sorted(favorite_genres.items(), key=lambda x: x[1], reverse=True)[:5]),
            'preferences': UserPreferencesSerializer(user.preferences).data,
        }
        
        return Response(dashboard_data)
    
    except Exception as e:
        logger.error(f"Error getting user dashboard: {e}")
        return Response(
            {'error': 'Failed to load dashboard'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account(request):
    """Delete user account"""
    try:
        user = request.user
        
        # Log account deletion
        UserActivity.objects.create(
            user=user,
            activity_type='account_deletion',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Delete user account
        user.delete()
        
        return Response({'message': 'Account deleted successfully'})
    
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        return Response(
            {'error': 'Failed to delete account'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_recommendations_history(request):
    """Get user's recommendation history"""
    from movies.models import RecommendationHistory
    from movies.serializers import RecommendationHistorySerializer
    
    history = RecommendationHistory.objects.filter(user=request.user)[:50]
    serializer = RecommendationHistorySerializer(history, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_recommendation_clicked(request):
    """Mark a recommendation as clicked"""
    from movies.models import RecommendationHistory
    
    recommendation_id = request.data.get('recommendation_id')
    if not recommendation_id:
        return Response(
            {'error': 'recommendation_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        recommendation = RecommendationHistory.objects.get(
            id=recommendation_id,
            user=request.user
        )
        recommendation.clicked = True
        recommendation.save()
        
        return Response({'message': 'Recommendation marked as clicked'})
    
    except RecommendationHistory.DoesNotExist:
        return Response(
            {'error': 'Recommendation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error marking recommendation as clicked: {e}")
        return Response(
            {'error': 'Failed to update recommendation'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )