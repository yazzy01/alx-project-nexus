# Complete API Testing Guide

## 🌐 **Step 1: Access API Documentation**

**URL:** http://127.0.0.1:8000/api/docs/

You should see a beautiful Swagger interface with all your endpoints organized.

---

## 🧪 **Step 2: Test Public Endpoints (No Authentication Required)**

### **2.1 Test Genres**
- **Endpoint:** `GET /api/v1/movies/genres/`
- **Click:** "Try it out" → "Execute"
- **Expected:** List of 19 movie genres from TMDb
- **Sample Response:**
```json
[
  {"id": 1, "tmdb_id": 28, "name": "Action"},
  {"id": 2, "tmdb_id": 12, "name": "Adventure"},
  {"id": 3, "tmdb_id": 16, "name": "Animation"}
]
```

### **2.2 Test Movie List**
- **Endpoint:** `GET /api/v1/movies/`
- **Click:** "Try it out" → "Execute"
- **Expected:** Paginated list of movies with posters, ratings, genres
- **Sample Response:**
```json
{
  "count": 80,
  "next": "http://127.0.0.1:8000/api/v1/movies/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "tmdb_id": 912649,
      "title": "Venom: The Last Dance",
      "vote_average": 6.4,
      "poster_url": "https://image.tmdb.org/t/p/w500/...",
      "genres": [{"name": "Action"}, {"name": "Adventure"}]
    }
  ]
}
```

### **2.3 Test Movie Details**
- **Endpoint:** `GET /api/v1/movies/{tmdb_id}/`
- **Use a tmdb_id from the previous response (e.g., 912649)**
- **Expected:** Detailed movie information

### **2.4 Test Recommendations**
- **Endpoint:** `GET /api/v1/movies/recommendations/`
- **Parameters to try:**
  - `type=popular` (default)
  - `type=trending`
  - `type=top_rated`
  - `type=upcoming`
- **Expected:** List of recommended movies

### **2.5 Test Movie Search**
- **Endpoint:** `POST /api/v1/movies/search/`
- **Request Body:**
```json
{
  "query": "Avengers",
  "page": 1
}
```
- **Expected:** Search results for "Avengers" movies

---

## 🔐 **Step 3: Test User Authentication**

### **3.1 Register a New User**
- **Endpoint:** `POST /api/v1/users/register/`
- **Request Body:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "testpass123",
  "password_confirm": "testpass123",
  "first_name": "Test",
  "last_name": "User"
}
```
- **Expected Response:**
```json
{
  "user": {
    "id": 2,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
  },
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
  "message": "User registered successfully"
}
```
- **IMPORTANT:** Copy the token from the response!

### **3.2 Test Login (Alternative)**
- **Endpoint:** `POST /api/v1/users/login/`
- **Request Body:**
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

---

## 🔑 **Step 4: Set Up Authentication for Protected Endpoints**

### **4.1 Add Authorization Header**
1. **Scroll to top of Swagger page**
2. **Click "Authorize" button** (lock icon)
3. **In the "Token" field, enter:** `Token your-token-here`
   - Example: `Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`
4. **Click "Authorize"**
5. **Click "Close"**

Now you can test protected endpoints!

---

## ⭐ **Step 5: Test Personal Features (Authentication Required)**

### **5.1 Add Movie to Favorites**
- **Endpoint:** `POST /api/v1/movies/favorites/`
- **Request Body:**
```json
{
  "movie_id": 1
}
```
- **Expected:** Movie added to favorites

### **5.2 View Favorites**
- **Endpoint:** `GET /api/v1/movies/favorites/`
- **Expected:** List of user's favorite movies

### **5.3 Rate a Movie**
- **Endpoint:** `POST /api/v1/movies/ratings/`
- **Request Body:**
```json
{
  "movie_id": 1,
  "rating": 4.5,
  "review": "Great movie! Really enjoyed it."
}
```
- **Expected:** Rating saved successfully

### **5.4 Add to Watchlist**
- **Endpoint:** `POST /api/v1/movies/watchlist/`
- **Request Body:**
```json
{
  "movie_id": 2
}
```

### **5.5 View User Profile**
- **Endpoint:** `GET /api/v1/users/profile/`
- **Expected:** User profile with stats

### **5.6 View User Dashboard**
- **Endpoint:** `GET /api/v1/users/dashboard/`
- **Expected:** User dashboard with favorites count, ratings, etc.

---

## 🎯 **Step 6: Advanced Testing**

### **6.1 Test Movie Filtering**
- **Endpoint:** `GET /api/v1/movies/`
- **Parameters to try:**
  - `genre=28` (Action movies)
  - `year=2024` (Movies from 2024)
  - `min_rating=7.0` (High-rated movies)
  - `search=Marvel` (Search in title)
  - `sort_by=rating` (Sort by rating)

### **6.2 Test Similar Movies**
- **Endpoint:** `GET /api/v1/movies/similar/`
- **Parameters:** `movie_id=912649`

### **6.3 Test User Activities**
- **Endpoint:** `GET /api/v1/users/activities/`
- **Expected:** List of user's recent activities

---

## ✅ **Step 7: Verification Checklist**

### **Public Endpoints Working:**
- [ ] Genres list loads (19 genres)
- [ ] Movies list loads (80+ movies with posters)
- [ ] Movie details show complete information
- [ ] Recommendations work for all types
- [ ] Search returns relevant results

### **Authentication Working:**
- [ ] User registration creates account and returns token
- [ ] Login returns valid token
- [ ] Authorization header accepts token
- [ ] Protected endpoints require authentication

### **Personal Features Working:**
- [ ] Can add movies to favorites
- [ ] Can rate movies (0.5-5.0 scale)
- [ ] Can add movies to watchlist
- [ ] User profile shows correct information
- [ ] Dashboard displays user stats

### **Data Quality:**
- [ ] Movies have real TMDb data (titles, posters, ratings)
- [ ] Genres are properly assigned to movies
- [ ] Poster URLs work and show images
- [ ] Release dates are formatted correctly
- [ ] Vote averages are realistic (0-10 scale)

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: "Authentication credentials were not provided"**
- **Solution:** Make sure you clicked "Authorize" and entered `Token your-token-here`

### **Issue 2: "Movie not found" when adding to favorites**
- **Solution:** Use a valid movie `id` from the movies list, not `tmdb_id`

### **Issue 3: Empty movie list**
- **Solution:** Run `python manage.py setup_initial_data` again

### **Issue 4: Poster images not loading**
- **Solution:** This is normal - TMDb poster URLs work but may be blocked by browser security

---

## 🎬 **Ready for Demo Recording?**

If all tests pass, you're ready to record your demo video! Your API has:
- ✅ **80 real movies** from TMDb
- ✅ **19 genres** properly categorized
- ✅ **Working authentication** system
- ✅ **Personal features** (favorites, ratings, watchlist)
- ✅ **Search and recommendations**
- ✅ **Professional API documentation**

## 🎯 **Demo Recording Tips:**

1. **Start with:** http://127.0.0.1:8000/api/docs/
2. **Show:** Beautiful Swagger documentation
3. **Test:** Public endpoints first (genres, movies, recommendations)
4. **Register:** A new user and get token
5. **Demonstrate:** Personal features (favorites, ratings)
6. **Highlight:** Real TMDb data integration
7. **End with:** User dashboard showing activity

Your Movie Recommendation Backend is **production-ready** and **demo-ready**! 🚀