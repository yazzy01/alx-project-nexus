from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserActivity, UserPreferences


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'activity_type', 'movie_id', 
        'timestamp', 'ip_address'
    ]
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username', 'activity_type', 'movie_id']
    readonly_fields = ['timestamp', 'ip_address', 'user_agent']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'activity_type', 'movie_id')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable adding activities manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing activities"""
        return False


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_notifications', 'recommendation_emails',
        'include_adult_content', 'preferred_language', 'profile_visibility'
    ]
    list_filter = [
        'email_notifications', 'recommendation_emails',
        'include_adult_content', 'preferred_language', 'profile_visibility'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Preferences', {
            'fields': ('email_notifications', 'recommendation_emails')
        }),
        ('Content Preferences', {
            'fields': ('include_adult_content', 'preferred_language')
        }),
        ('Recommendation Settings', {
            'fields': (
                'enable_collaborative_filtering',
                'enable_content_based_filtering',
                'recommendation_diversity'
            )
        }),
        ('Privacy Settings', {
            'fields': ('profile_visibility',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Extend the default User admin to show related information
class UserPreferencesInline(admin.StackedInline):
    model = UserPreferences
    can_delete = False
    verbose_name_plural = 'User Preferences'


class ExtendedUserAdmin(BaseUserAdmin):
    inlines = (UserPreferencesInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)