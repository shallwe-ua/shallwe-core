from django.urls import path

from .views import LocationSearchView

urlpatterns = [
    path('search/', LocationSearchView.as_view(), name='location-search'),
]
