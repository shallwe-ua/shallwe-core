from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView as RestAuthLogoutView
from django.conf import settings
from rest_framework.permissions import IsAuthenticated


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.SHALLWE_CONF_GOOGLE_CALLBACK_URL
    client_class = OAuth2Client


class LogoutView(RestAuthLogoutView):
    permission_classes = [IsAuthenticated]
