from movies.services import tmdb_service
print("Testing TMDb API...")
popular = tmdb_service.get_popular_movies()
if popular:
    print(f"✅ Got {len(popular.get('results', []))} movies!")
    print(f"First movie: {popular['results'][0]['title']}")
else:
    print("❌ API failed")
exit()