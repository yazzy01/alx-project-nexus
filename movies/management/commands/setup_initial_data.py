from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.services import tmdb_service
from movies.models import Genre
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Setup initial data for the movie recommendation system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-movies',
            action='store_true',
            help='Skip syncing movies, only sync genres',
        )
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting initial data setup...')
        )
        
        # Create superuser if requested
        if options['create_superuser']:
            self.create_superuser()
        
        # Sync genres from TMDb
        self.sync_genres()
        
        # Sync movies if not skipped
        if not options['skip_movies']:
            self.sync_initial_movies()
        
        self.stdout.write(
            self.style.SUCCESS('Initial data setup completed!')
        )
    
    def create_superuser(self):
        """Create a superuser account"""
        self.stdout.write('Creating superuser account...')
        
        if User.objects.filter(username='admin').exists():
            self.stdout.write(
                self.style.WARNING('Superuser "admin" already exists')
            )
            return
        
        try:
            User.objects.create_superuser(
                username='admin',
                email='admin@movierecommendation.local',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS('Superuser created successfully!')
            )
            self.stdout.write('Username: admin')
            self.stdout.write('Password: admin123')
            self.stdout.write(
                self.style.WARNING('Please change the password in production!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create superuser: {e}')
            )
    
    def sync_genres(self):
        """Sync genres from TMDb API"""
        self.stdout.write('Syncing genres from TMDb...')
        
        try:
            success = tmdb_service.sync_genres_to_db()
            if success:
                genre_count = Genre.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully synced {genre_count} genres')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to sync genres from TMDb')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing genres: {e}')
            )
    
    def sync_initial_movies(self):
        """Sync initial set of movies from TMDb"""
        self.stdout.write('Syncing initial movies from TMDb...')
        
        movie_categories = [
            ('popular', 'Popular Movies'),
            ('top_rated', 'Top Rated Movies'),
            ('trending', 'Trending Movies'),
            ('upcoming', 'Upcoming Movies'),
        ]
        
        total_synced = 0
        
        for category, description in movie_categories:
            self.stdout.write(f'Syncing {description.lower()}...')
            
            try:
                if category == 'popular':
                    data = tmdb_service.get_popular_movies()
                elif category == 'top_rated':
                    data = tmdb_service.get_top_rated_movies()
                elif category == 'trending':
                    data = tmdb_service.get_trending_movies()
                elif category == 'upcoming':
                    data = tmdb_service.get_upcoming_movies()
                
                if data and 'results' in data:
                    movies = tmdb_service.sync_movies_to_db(data['results'])
                    synced_count = len(movies)
                    total_synced += synced_count
                    self.stdout.write(
                        self.style.SUCCESS(f'Synced {synced_count} {description.lower()}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'No data received for {description.lower()}')
                    )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error syncing {description.lower()}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Total movies synced: {total_synced}')
        )
    
    def create_sample_users(self):
        """Create sample users for testing"""
        self.stdout.write('Creating sample users...')
        
        sample_users = [
            {
                'username': 'moviefan1',
                'email': 'moviefan1@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'testpass123'
            },
            {
                'username': 'cinephile',
                'email': 'cinephile@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'password': 'testpass123'
            },
        ]
        
        created_count = 0
        for user_data in sample_users:
            username = user_data['username']
            if not User.objects.filter(username=username).exists():
                try:
                    User.objects.create_user(**user_data)
                    created_count += 1
                    self.stdout.write(f'Created user: {username}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to create user {username}: {e}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User {username} already exists')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} sample users')
        )