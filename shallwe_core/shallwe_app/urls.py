from django.conf import settings
from django.urls import path

from .views import LandingView, SetupView, SearchView, ContactsView, SettingsView


urlpatterns = [
    path('', LandingView.as_view(), name='page-landing'),
    path('setup/', SetupView.as_view(), name='page-setup'),
    path('search/', SearchView.as_view(), name='page-search'),
    path('contacts/', ContactsView.as_view(), name='page-contacts'),
    path('settings/', SettingsView.as_view(), name='page-settings'),
]

if settings.SHALLWE_CONF_ENV_MODE == 'DEV':
    from .test_views import SampleAuthenticatedView, SampleGeneralView
    urlpatterns += [
        path('test-api-protected/', SampleAuthenticatedView.as_view(), name='test-api-protected'),
        path('test-api-unprotected/', SampleGeneralView.as_view(), name='test-api-unprotected'),
    ]
