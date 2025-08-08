from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import UserActivity, UserPreferences


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value
    
    def create(self, validated_data):
        """Create a new user"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate user credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Must include username and password")
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    def get_full_name(self, obj):
        """Get user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def validate_email(self, value):
        """Validate email uniqueness (excluding current user)"""
        user = self.instance
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def save(self):
        """Save new password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for UserPreferences model"""
    
    class Meta:
        model = UserPreferences
        fields = [
            'email_notifications', 'recommendation_emails',
            'include_adult_content', 'preferred_language',
            'enable_collaborative_filtering', 'enable_content_based_filtering',
            'recommendation_diversity', 'profile_visibility',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_recommendation_diversity(self, value):
        """Validate recommendation diversity is between 0 and 1"""
        if value < 0.0 or value > 1.0:
            raise serializers.ValidationError(
                "Recommendation diversity must be between 0.0 and 1.0"
            )
        return value


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for UserActivity model"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'activity_type', 'movie_id',
            'metadata', 'timestamp', 'ip_address'
        ]
        read_only_fields = ['id', 'user', 'timestamp']


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    total_favorites = serializers.IntegerField()
    total_watchlist = serializers.IntegerField()
    total_ratings = serializers.IntegerField()
    average_rating = serializers.FloatField()
    total_activities = serializers.IntegerField()
    favorite_genres = serializers.ListField(child=serializers.CharField())
    recent_activities = UserActivitySerializer(many=True)
    
    def to_representation(self, instance):
        """Custom representation for user stats"""
        user = instance
        
        # Calculate statistics
        favorite_movies = user.favorite_movies.all()
        watchlist_movies = user.watchlist.all()
        ratings = user.movie_ratings.all()
        activities = user.activities.all()[:10]  # Last 10 activities
        
        # Calculate average rating
        avg_rating = 0.0
        if ratings.exists():
            avg_rating = sum(r.rating for r in ratings) / len(ratings)
        
        # Get favorite genres (from rated movies)
        favorite_genres = []
        if ratings.exists():
            genre_counts = {}
            for rating in ratings:
                for genre in rating.movie.genres.all():
                    genre_counts[genre.name] = genre_counts.get(genre.name, 0) + 1
            
            # Sort by count and get top 5
            favorite_genres = sorted(
                genre_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            favorite_genres = [genre[0] for genre in favorite_genres]
        
        return {
            'total_favorites': favorite_movies.count(),
            'total_watchlist': watchlist_movies.count(),
            'total_ratings': ratings.count(),
            'average_rating': round(avg_rating, 2),
            'total_activities': activities.count(),
            'favorite_genres': favorite_genres,
            'recent_activities': UserActivitySerializer(activities, many=True).data
        }