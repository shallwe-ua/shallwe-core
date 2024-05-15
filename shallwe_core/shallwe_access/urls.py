from django.urls import path

from .views import GetProfileStatusView


urlpatterns = [
    path('profile-status', GetProfileStatusView.as_view(), name='profile-status'),
]
