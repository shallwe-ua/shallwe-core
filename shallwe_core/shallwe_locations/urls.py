from django.urls import path

from .views import LocationSearchView

urlpatterns = [
    path('', LocationSearchView.as_view(), name='location-search'),
]
