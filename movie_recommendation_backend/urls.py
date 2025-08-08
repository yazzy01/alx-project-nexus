"""
URL configuration for movie_recommendation_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

def redirect_to_frontend(request):
    """Redirect root URL to frontend"""
    return redirect('/frontend/')

# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Movie Recommendation API",
        default_version='v1',
        description="A comprehensive movie recommendation backend API built with Django REST Framework. "
                   "This API provides endpoints for movie discovery, user authentication, favorites management, "
                   "ratings, watchlists, and personalized recommendations using The Movie Database (TMDb) API.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@movierecommendation.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root URL redirect
    path('', redirect_to_frontend, name='home'),
    
    # Frontend
    path('frontend/', TemplateView.as_view(template_name='index.html'), name='frontend'),
    
    # Admin interface
    path("admin/", admin.site.urls),
    
    # API endpoints
    path('api/v1/movies/', include('movies.urls')),
    path('api/v1/users/', include('users.urls')),
    
    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
