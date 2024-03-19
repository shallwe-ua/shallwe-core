from django.urls import path

from .views import ProfileAPIView, ProfileVisibilityAPIView

urlpatterns = [
    path('me/', ProfileAPIView.as_view(), name='profile-me'),
    path('visibility/', ProfileVisibilityAPIView.as_view(), name='profile-visibility')
]
