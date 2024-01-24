from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create a test user with a fixed token'

    def handle(self, *args, **options):
        # Replace 'your_username' with the desired username
        username = 'qa_test_user'
        email = 'qa_test_user@example.com'
        password = settings.SHALLWE_CONF_QA_TEST_USER_PASS

        # Create or get the user
        user, created = User.objects.get_or_create(username=username, email=email)
        if not created:
            self.stdout.write(self.style.SUCCESS(f'Test user "{user.username}" already exists'))
            return
        elif created:
            user.set_password(password)
            user.save()

        # Create or update the token
        token_value = settings.SHALLWE_CONF_QA_TEST_USER_TOKEN
        token, created = Token.objects.get_or_create(user=user, key=token_value)
        token.save()

        # Print the results
        self.stdout.write(self.style.SUCCESS(f'Test user "{user.username}" created. See token in adminpanel'))
