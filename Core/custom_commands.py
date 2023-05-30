from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with a specified email address.'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address for the superuser.')
        parser.add_argument('--username', type=str, help='Username for the superuser.')
        parser.add_argument('--password', type=str, help='Password for the superuser.')

    def handle(self, *args, **options):
        email = options['email']
        username = options['username']
        password = options['password']

        if not email or not username or not password:
            self.stdout.write(self.style.ERROR('Please provide --email, --username, and --password options.'))
            return

        User.objects.create_superuser(email=email, username=username, password=password)
        self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
