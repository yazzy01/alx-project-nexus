# Movie Recommendation Backend - ALX Project Nexus

[![Django](https://img.shields.io/badge/Django-5.2.5-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![DRF](https://img.shields.io/badge/DRF-3.16.0-red.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive movie recommendation backend API built with Django REST Framework, featuring user authentication, movie discovery, personalized recommendations, and comprehensive API documentation.

## 🎬 Project Overview

This project is part of the **ALX Project Nexus - ProDev Backend Engineering Program** and demonstrates real-world backend development practices including:

- **RESTful API Development** with Django REST Framework
- **Third-party API Integration** with The Movie Database (TMDb)
- **Caching Strategies** using Redis for performance optimization
- **User Authentication & Authorization** with Token-based authentication
- **Background Task Processing** with Celery
- **Comprehensive API Documentation** with Swagger/OpenAPI
- **Database Design & Optimization** with proper indexing and relationships

## 🚀 Key Features

### 🎭 Movie Management
- **Movie Discovery**: Browse trending, popular, top-rated, and upcoming movies
- **Advanced Search**: Search movies by title, genre, year, and rating
- **Movie Details**: Comprehensive movie information with posters and backdrops
- **Genre Filtering**: Filter movies by multiple genres

### 👤 User Management
- **User Registration & Authentication**: Secure user registration and login
- **User Profiles**: Customizable user profiles with preferences
- **Activity Tracking**: Track user interactions and behavior
- **Privacy Settings**: Configurable privacy and notification preferences

### ⭐ Personal Features
- **Favorites**: Save and manage favorite movies
- **Watchlist**: Create and manage personal watchlists
- **Movie Ratings**: Rate and review movies
- **Personalized Recommendations**: AI-powered movie suggestions

### 🔧 Technical Features
- **Caching**: Redis-based caching for improved performance
- **Background Tasks**: Celery for asynchronous processing
- **API Documentation**: Interactive Swagger documentation
- **Error Handling**: Comprehensive error handling and logging
- **Data Validation**: Robust input validation and sanitization

## 🛠 Technology Stack

### Backend Framework
- **Django 5.2.5**: Web framework
- **Django REST Framework 3.16.0**: API development
- **Python 3.8+**: Programming language

### Database & Caching
- **SQLite**: Default database (easily configurable to PostgreSQL)
- **Redis**: Caching and session storage
- **Django ORM**: Database abstraction layer

### Background Processing
- **Celery**: Asynchronous task processing
- **Redis**: Message broker for Celery

### API & Documentation
- **drf-yasg**: Swagger/OpenAPI documentation
- **Django CORS Headers**: Cross-origin resource sharing

### External Services
- **TMDb API**: Movie data source
- **Requests**: HTTP client for API calls

## 📋 Prerequisites

Before running this project, make sure you have:

- **Python 3.8+** installed
- **Redis** server (for caching and Celery)
- **Git** for version control
- **TMDb API Key** (free registration at [TMDb](https://www.themoviedb.org/))

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yazzy01/alx-project-nexus.git
cd alx-project-nexus
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your configuration
# Add your TMDb API key and other settings
```

### 5. Set Up Database
```bash
# Run database migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Set up initial data (genres and sample movies)
python manage.py setup_initial_data --create-superuser
```

### 6. Start Redis Server
```bash
# Make sure Redis is running on localhost:6379
redis-server
```

### 7. Start the Development Server
```bash
# Start Django development server
python manage.py runserver

# In another terminal, start Celery worker (optional)
celery -A movie_recommendation_backend worker --loglevel=info
```

### 8. Access the Application
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Interface**: http://localhost:8000/admin/
- **API Base URL**: http://localhost:8000/api/v1/

## 📚 API Documentation

The API is fully documented using Swagger/OpenAPI. Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### 🔑 Authentication

The API uses Token-based authentication. To access protected endpoints:

1. **Register a new user**:
   ```bash
   POST /api/v1/users/register/
   ```

2. **Login to get token**:
   ```bash
   POST /api/v1/users/login/
   ```

3. **Use token in headers**:
   ```bash
   Authorization: Token your-token-here
   ```

### 📖 Main API Endpoints

#### Movies
- `GET /api/v1/movies/` - List movies with filtering
- `GET /api/v1/movies/{tmdb_id}/` - Get movie details
- `GET /api/v1/movies/recommendations/` - Get recommendations
- `POST /api/v1/movies/search/` - Search movies
- `GET /api/v1/movies/genres/` - List genres

#### User Management
- `POST /api/v1/users/register/` - Register new user
- `POST /api/v1/users/login/` - User login
- `POST /api/v1/users/logout/` - User logout
- `GET /api/v1/users/profile/` - Get user profile
- `GET /api/v1/users/dashboard/` - User dashboard

#### Personal Features
- `GET /api/v1/movies/favorites/` - User's favorite movies
- `POST /api/v1/movies/favorites/` - Add to favorites
- `GET /api/v1/movies/watchlist/` - User's watchlist
- `GET /api/v1/movies/ratings/` - User's movie ratings

## 🏗 Project Structure

```
alx-project-nexus/
├── movie_recommendation_backend/    # Django project settings
│   ├── settings.py                 # Main settings
│   ├── urls.py                     # URL configuration
│   ├── celery.py                   # Celery configuration
│   └── wsgi.py                     # WSGI configuration
├── movies/                         # Movies app
│   ├── models.py                   # Database models
│   ├── views.py                    # API views
│   ├── serializers.py              # Data serializers
│   ├── services.py                 # Business logic
│   ├── tasks.py                    # Celery tasks
│   ├── admin.py                    # Admin configuration
│   └── urls.py                     # App URLs
├── users/                          # Users app
│   ├── models.py                   # User models
│   ├── views.py                    # User views
│   ├── serializers.py              # User serializers
│   └── urls.py                     # User URLs
├── logs/                           # Application logs
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
└── README.md                      # This file
```

## 🗄 Database Schema

### Core Models

#### Movie
- Stores movie information from TMDb
- Includes ratings, popularity, genres
- Optimized with database indexes

#### User Extensions
- **UserProfile**: Extended user information
- **UserPreferences**: User settings and preferences
- **UserActivity**: Activity tracking

#### User Interactions
- **FavoriteMovie**: User's favorite movies
- **MovieRating**: User movie ratings and reviews
- **Watchlist**: User's watchlist
- **RecommendationHistory**: Recommendation tracking

## ⚡ Performance Optimization

### Caching Strategy
- **Redis Caching**: API responses cached for improved performance
- **Database Query Optimization**: Efficient queries with select_related
- **Background Processing**: Heavy tasks processed asynchronously

### Database Optimization
- **Indexes**: Strategic database indexes for common queries
- **Query Optimization**: Optimized ORM queries
- **Connection Pooling**: Efficient database connections

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (for PostgreSQL)
DB_NAME=movie_recommendation_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://localhost:6379/0

# TMDb API Settings
TMDB_API_KEY=your-tmdb-api-key-here
TMDB_BASE_URL=https://api.themoviedb.org/3

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DELTA=3600
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📦 Deployment

### Production Checklist

1. **Environment Configuration**:
   - Set `DEBUG=False`
   - Configure production database (PostgreSQL)
   - Set up proper Redis configuration
   - Configure allowed hosts

2. **Security**:
   - Use strong secret keys
   - Enable HTTPS
   - Configure CORS properly
   - Set up proper authentication

3. **Performance**:
   - Configure caching
   - Set up Celery workers
   - Optimize database queries
   - Enable compression

### Docker Deployment (Optional)

```dockerfile
# Dockerfile example
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'feat: add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Commit Convention
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation updates
- `perf:` Performance improvements
- `refactor:` Code refactoring
- `test:` Adding tests

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ALX ProDev Program**: For providing comprehensive backend engineering education
- **The Movie Database (TMDb)**: For providing the movie data API
- **Django Community**: For the excellent framework and documentation
- **Open Source Community**: For the amazing tools and libraries

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/yazzy01/alx-project-nexus/issues)
- **Discord**: Join `#ProDevProjectNexus` channel
- **Documentation**: Check the API docs at `/api/docs/`

---

**Built By Yassir Rzigui with ❤️ for the ALX ProDev Backend Engineering Program**

*This project demonstrates real-world backend development practices and serves as a portfolio piece showcasing advanced Django REST Framework skills.*
