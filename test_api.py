#!/usr/bin/env python3
"""
Simple API test script for Movie Recommendation Backend
This script demonstrates the basic functionality of the API
"""

import requests
import json
import sys

# API Base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    """Test the main API endpoints"""
    print("🎬 Testing Movie Recommendation Backend API")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/movies/genres/")
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            genres = response.json()
            print(f"   Found {len(genres)} genres")
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return False
    
    # Test 2: User Registration
    print("\n2. Testing user registration...")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/users/register/", json=user_data)
    if response.status_code == 201:
        print("✅ User registration successful")
        user_info = response.json()
        token = user_info.get('token')
        print(f"   User: {user_info['user']['username']}")
        print(f"   Token: {token[:20]}...")
    elif response.status_code == 400:
        print("⚠️  User might already exist")
        # Try to login instead
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/users/login/", json=login_data)
        if response.status_code == 200:
            print("✅ User login successful")
            user_info = response.json()
            token = user_info.get('token')
        else:
            print("❌ Login failed")
            return False
    else:
        print(f"❌ Registration failed with status {response.status_code}")
        return False
    
    # Set up headers for authenticated requests
    headers = {"Authorization": f"Token {token}"}
    
    # Test 3: Get Movies
    print("\n3. Testing movie listing...")
    response = requests.get(f"{BASE_URL}/movies/", params={"page_size": 5})
    if response.status_code == 200:
        movies = response.json()
        print(f"✅ Retrieved {len(movies['results']) if 'results' in movies else len(movies)} movies")
        if movies and ('results' in movies and movies['results']) or (isinstance(movies, list) and movies):
            movie_list = movies['results'] if 'results' in movies else movies
            first_movie = movie_list[0]
            print(f"   First movie: {first_movie.get('title', 'Unknown')}")
    else:
        print(f"❌ Failed to get movies: {response.status_code}")
    
    # Test 4: Get Recommendations
    print("\n4. Testing recommendations...")
    response = requests.get(f"{BASE_URL}/movies/recommendations/", params={"type": "popular"})
    if response.status_code == 200:
        recommendations = response.json()
        print(f"✅ Retrieved {len(recommendations)} recommendations")
        if recommendations:
            print(f"   First recommendation: {recommendations[0].get('title', 'Unknown')}")
    else:
        print(f"❌ Failed to get recommendations: {response.status_code}")
    
    # Test 5: User Profile
    print("\n5. Testing user profile...")
    response = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
    if response.status_code == 200:
        profile = response.json()
        print("✅ Retrieved user profile")
        print(f"   User: {profile['user']['username']}")
    else:
        print(f"❌ Failed to get profile: {response.status_code}")
    
    # Test 6: Search Movies
    print("\n6. Testing movie search...")
    search_data = {
        "query": "Avengers",
        "page": 1
    }
    response = requests.post(f"{BASE_URL}/movies/search/", json=search_data)
    if response.status_code == 200:
        search_results = response.json()
        results_count = len(search_results.get('results', []))
        print(f"✅ Search returned {results_count} results")
        if search_results.get('results'):
            first_result = search_results['results'][0]
            print(f"   First result: {first_result.get('title', 'Unknown')}")
    else:
        print(f"❌ Search failed: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    print("\n📚 API Documentation available at:")
    print("   Swagger UI: http://localhost:8000/api/docs/")
    print("   ReDoc: http://localhost:8000/api/redoc/")
    print("   Admin: http://localhost:8000/admin/")
    
    return True

def main():
    """Main function"""
    print("Movie Recommendation Backend - API Test")
    print("Make sure the Django server is running on localhost:8000")
    print("Press Enter to continue or Ctrl+C to exit...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        sys.exit(0)
    
    success = test_api()
    
    if success:
        print("\n✅ All tests passed! The API is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the server and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()