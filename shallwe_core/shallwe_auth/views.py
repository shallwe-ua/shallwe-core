from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView as RestAuthLogoutView
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class GoogleLoginView(SocialLoginView):
    """Notice: In case of problems with code validation, the second option is access_token + id_token = no problems"""
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.SHALLWE_GLOBAL_OAUTH_REDIRECT_URI
    client_class = OAuth2Client


class LogoutView(RestAuthLogoutView):
    permission_classes = [IsAuthenticated]


class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response(status=204)
