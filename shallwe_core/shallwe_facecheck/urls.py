from django.urls import path

from .views import FaceDetectionView

urlpatterns = [
    path('', FaceDetectionView.as_view(), name='facecheck'),
]
