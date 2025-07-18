from django.conf import settings
from django.urls import path
from .views import GoogleLoginView, LogoutView, DeleteUserView


urlpatterns = [
    path('login/google/', GoogleLoginView.as_view(), name='google-auth'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', DeleteUserView.as_view(), name='delete-user')
]


if settings.SHALLWE_GLOBAL_ENV_MODE in ('DEV', 'QA'):
    from .test_views import SampleAuthenticatedView, SampleGeneralView
    urlpatterns += [
        path('test-api-protected/', SampleAuthenticatedView.as_view(), name='test-api-protected'),
        path('test-api-unprotected/', SampleGeneralView.as_view(), name='test-api-unprotected'),
    ]
