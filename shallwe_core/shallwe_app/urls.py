from django.urls import path

from .views import LandingView, SetupView, SearchView, ContactsView, SettingsView


urlpatterns = [
    path('', LandingView.as_view(), name='page-landing'),
    path('setup/', SetupView.as_view(), name='page-setup'),
    path('search/', SearchView.as_view(), name='page-search'),
    path('contacts/', ContactsView.as_view(), name='page-contacts'),
    path('settings/', SettingsView.as_view(), name='page-settings'),
]
