from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .facecheck import check_face_minified_temp
from . import formatcheck


class FaceDetectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        uploaded_image = request.data.get('image')

        # Check upload
        if not uploaded_image:
            return Response({'error': 'No image provided'}, status=400)

        # Todo: actually all this stuff could do a DRF serializer - refactor later
        # Check format
        clean_result = self._try_clean_image(uploaded_image)
        if not clean_result['success']:
            return Response({'error': clean_result['error']}, status=400)

        # Check face
        is_face_detected = check_face_minified_temp(clean_result['image'])
        return Response({'success': is_face_detected})

    def _try_clean_image(self, uploaded_image: InMemoryUploadedFile):
        result = {
            'image': None,
            'success': False,
            'error': ''
        }
        try:
            result['image'] = formatcheck.clean_image(uploaded_image)
            result['success'] = True
        except (formatcheck.ImageValidationError, ValueError) as e:
            result['error'] = str(e)
        return result
