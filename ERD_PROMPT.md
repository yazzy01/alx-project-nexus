# ERD Diagram Prompt for Movie Recommendation Backend

## Instructions for ERD AI Tool:
Create a comprehensive Entity Relationship Diagram (ERD) for a Movie Recommendation Backend system with the following entities and relationships:

## ENTITIES AND ATTRIBUTES:

### 1. **User** (Django built-in)
- id (PK, Integer, Auto-increment)
- username (String, Unique, Max 150 chars)
- email (String, Unique)
- first_name (String, Max 150 chars)
- last_name (String, Max 150 chars)
- password (String, Hashed)
- is_active (Boolean, Default: True)
- is_staff (Boolean, Default: False)
- date_joined (DateTime, Auto-add)
- last_login (DateTime, Nullable)

### 2. **Genre**
- id (PK, Integer, Auto-increment)
- tmdb_id (Integer, Unique)
- name (String, Max 100 chars)

### 3. **Movie**
- id (PK, Integer, Auto-increment)
- tmdb_id (Integer, Unique)
- title (String, Max 255 chars)
- overview (Text, Nullable)
- release_date (Date, Nullable)
- poster_path (String, Max 255 chars, Nullable)
- backdrop_path (String, Max 255 chars, Nullable)
- vote_average (Float, Default: 0.0, Range: 0-10)
- vote_count (Integer, Default: 0)
- popularity (Float, Default: 0.0)
- adult (Boolean, Default: False)
- original_language (String, Max 10 chars)
- original_title (String, Max 255 chars)
- created_at (DateTime, Auto-add)
- updated_at (DateTime, Auto-update)

### 4. **UserProfile**
- id (PK, Integer, Auto-increment)
- user_id (FK to User, One-to-One)
- date_joined (DateTime, Auto-add)

### 5. **UserPreferences**
- id (PK, Integer, Auto-increment)
- user_id (FK to User, One-to-One)
- email_notifications (Boolean, Default: True)
- recommendation_emails (Boolean, Default: True)
- include_adult_content (Boolean, Default: False)
- preferred_language (String, Max 10 chars, Default: 'en')
- enable_collaborative_filtering (Boolean, Default: True)
- enable_content_based_filtering (Boolean, Default: True)
- recommendation_diversity (Float, Default: 0.5, Range: 0-1)
- profile_visibility (String, Choices: 'public', 'friends', 'private', Default: 'public')
- created_at (DateTime, Auto-add)
- updated_at (DateTime, Auto-update)

### 6. **FavoriteMovie**
- id (PK, Integer, Auto-increment)
- user_id (FK to User)
- movie_id (FK to Movie)
- added_at (DateTime, Auto-add)
- **Unique Constraint**: (user_id, movie_id)

### 7. **MovieRating**
- id (PK, Integer, Auto-increment)
- user_id (FK to User)
- movie_id (FK to Movie)
- rating (Float, Range: 0.5-5.0)
- review (Text, Nullable)
- created_at (DateTime, Auto-add)
- updated_at (DateTime, Auto-update)
- **Unique Constraint**: (user_id, movie_id)

### 8. **Watchlist**
- id (PK, Integer, Auto-increment)
- user_id (FK to User)
- movie_id (FK to Movie)
- added_at (DateTime, Auto-add)
- **Unique Constraint**: (user_id, movie_id)

### 9. **UserActivity**
- id (PK, Integer, Auto-increment)
- user_id (FK to User)
- activity_type (String, Choices: 'login', 'logout', 'view_movie', 'rate_movie', 'add_favorite', 'remove_favorite', 'add_watchlist', 'remove_watchlist', 'search', 'view_recommendations')
- movie_id (Integer, Nullable, TMDb movie ID)
- metadata (JSON, Default: {})
- timestamp (DateTime, Auto-add)
- ip_address (IP Address, Nullable)
- user_agent (Text, Nullable)

### 10. **RecommendationHistory**
- id (PK, Integer, Auto-increment)
- user_id (FK to User)
- movie_id (FK to Movie)
- recommendation_type (String, Choices: 'trending', 'popular', 'genre_based', 'collaborative', 'content_based')
- score (Float, Default: 0.0)
- clicked (Boolean, Default: False)
- created_at (DateTime, Auto-add)

## RELATIONSHIPS:

### **One-to-One Relationships:**
1. **User ↔ UserProfile**: Each user has exactly one profile
2. **User ↔ UserPreferences**: Each user has exactly one preferences record

### **One-to-Many Relationships:**
1. **User → FavoriteMovie**: One user can have many favorite movies
2. **Movie → FavoriteMovie**: One movie can be favorited by many users
3. **User → MovieRating**: One user can rate many movies
4. **Movie → MovieRating**: One movie can be rated by many users
5. **User → Watchlist**: One user can have many movies in watchlist
6. **Movie → Watchlist**: One movie can be in many users' watchlists
7. **User → UserActivity**: One user can have many activities
8. **User → RecommendationHistory**: One user can have many recommendation records
9. **Movie → RecommendationHistory**: One movie can appear in many recommendation records

### **Many-to-Many Relationships:**
1. **Movie ↔ Genre**: Movies can have multiple genres, genres can be associated with multiple movies
2. **UserProfile ↔ Genre**: Users can have multiple favorite genres (through UserProfile)

### **Indexes (for performance):**
- Movie: tmdb_id, release_date, vote_average, popularity
- UserActivity: (user_id, activity_type), timestamp, movie_id
- RecommendationHistory: (user_id, recommendation_type), created_at

## DIAGRAM REQUIREMENTS:

1. **Use standard ERD notation** with:
   - Rectangles for entities
   - Diamonds for relationships
   - Ovals for attributes
   - Lines connecting entities with cardinality indicators

2. **Show cardinality** clearly:
   - 1:1 for one-to-one relationships
   - 1:M for one-to-many relationships
   - M:N for many-to-many relationships

3. **Highlight Primary Keys** (underlined or bold)
4. **Show Foreign Keys** with FK notation
5. **Include unique constraints** where specified
6. **Use clear, readable layout** with proper spacing
7. **Color coding** (optional):
   - Core entities (User, Movie, Genre) in blue
   - User interaction entities (FavoriteMovie, MovieRating, Watchlist) in green
   - System entities (UserActivity, RecommendationHistory) in orange
   - User profile entities (UserProfile, UserPreferences) in purple

## ADDITIONAL NOTES:
- This is for a Django-based Movie Recommendation API
- The system integrates with TMDb (The Movie Database) API
- Focus on showing the relationships clearly for database design documentation
- The diagram should be suitable for technical documentation and presentation to stakeholders

Please create a professional, clean ERD diagram that clearly shows all these entities, their attributes, and relationships.