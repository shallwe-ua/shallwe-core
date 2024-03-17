from django.conf import settings
from django.urls import path
from .views import GoogleLoginView, LogoutView


urlpatterns = [
    path('login/google/', GoogleLoginView.as_view(), name='google-auth'),
    path('logout/', LogoutView.as_view(), name='logout')
]


if settings.SHALLWE_CONF_ENV_MODE in ('DEV', 'QA'):
    from .test_views import SampleAuthenticatedView, SampleGeneralView
    urlpatterns += [
        path('test-api-protected/', SampleAuthenticatedView.as_view(), name='test-api-protected'),
        path('test-api-unprotected/', SampleGeneralView.as_view(), name='test-api-unprotected'),
    ]
