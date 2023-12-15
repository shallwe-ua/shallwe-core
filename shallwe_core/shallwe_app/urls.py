from django.urls import path

from .views import LandingView, SetupView, SearchView, ContactsView, SettingsView

import environ


env = environ.Env()
environ.Env.read_env()


urlpatterns = [
    path('', LandingView.as_view(), name='page-landing'),
    path('setup/', SetupView.as_view(), name='page-setup'),
    path('search/', SearchView.as_view(), name='page-search'),
    path('contacts/', ContactsView.as_view(), name='page-contacts'),
    path('settings/', SettingsView.as_view(), name='page-settings'),
]

if env('SHALLWE_BACKEND_MODE') == 'DEV':
    from .test_views import SampleAuthenticatedView, SampleGeneralView
    urlpatterns += [
        path('test-auth/', SampleAuthenticatedView.as_view(), name='test-auth'),
        path('test-gen/', SampleGeneralView.as_view(), name='test-gen'),
    ]
