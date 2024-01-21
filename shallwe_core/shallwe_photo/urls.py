from django.urls import path

from .views import FaceDetectionView

urlpatterns = [
    path('facecheck/', FaceDetectionView.as_view(), name='facecheck'),
]
