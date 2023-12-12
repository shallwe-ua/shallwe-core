from django.urls import path
from .views import GoogleLoginView
from dj_rest_auth.views import LogoutView


urlpatterns = [
    path('login/google/', GoogleLoginView.as_view(), name='google-auth'),
    path('logout/', LogoutView.as_view(), name='logout')
]
