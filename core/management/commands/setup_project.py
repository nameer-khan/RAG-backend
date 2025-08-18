from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up the RAG Chat project with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up RAG Chat project...')
        
        try:
            # Create default site
            site, created = Site.objects.get_or_create(
                id=1,
                defaults={
                    'domain': 'localhost:8000',
                    'name': 'RAG Chat'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created default site'))
            else:
                self.stdout.write('Default site already exists')
            
            # Create superuser if it doesn't exist
            if not User.objects.filter(is_superuser=True).exists():
                self.stdout.write('Creating superuser...')
                username = 'admin'
                email = 'admin@ragchat.com'
                password = 'admin123'
                
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created superuser: {username} / {password}'
                    )
                )
            else:
                self.stdout.write('Superuser already exists')
            
            # Create system user for API key authentication
            system_user, created = User.objects.get_or_create(
                username='system_api_user',
                defaults={
                    'email': 'system@api.com',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created system API user'))
            else:
                self.stdout.write('System API user already exists')
            
            self.stdout.write(
                self.style.SUCCESS('Project setup completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up project: {str(e)}')
            )
            logger.error(f'Project setup failed: {str(e)}')
