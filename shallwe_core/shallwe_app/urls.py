from django.urls import path

from .views import LandingView, SampleRequireSessionLoginView
from .test_views import SampleAuthenticatedView, SampleGeneralView


urlpatterns = [
    path('sample-auth/', SampleAuthenticatedView.as_view(), name='sample-auth-api'),
    path('sample-nonauth/', SampleGeneralView.as_view(), name='sample-nonauth-api'),
    path('', LandingView.as_view(), name='landing'),
    path('sample-auth-page/', SampleRequireSessionLoginView.as_view(), name='sample-auth-page')
]
