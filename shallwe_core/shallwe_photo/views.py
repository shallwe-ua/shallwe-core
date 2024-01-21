from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import tempfile

from .facecheck import check_face
from . import formatcheck


class FaceDetectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        uploaded_image = request.data.get('image')

        # Check upload
        if not uploaded_image:
            return Response({'error': 'No image provided'}, status=400)

        # Check format
        clean_result = self._try_clean_image(uploaded_image)
        if not clean_result['success']:
            return Response({'error': clean_result['error']}, status=400)

        # Check face
        is_face_detected = self._check_face_in_mini_temp(clean_result['image'])
        return Response({'success': is_face_detected})

    def _try_clean_image(self, uploaded_image):
        result = {
            'image': None,
            'success': False,
            'error': ''
        }
        try:
            result['image'] = formatcheck.PhotoValidator.clean_image(uploaded_image)
            result['success'] = True
        except (formatcheck.InvalidImageFormatError, ValueError) as e:
            result['error'] = str(e)
        return result

    def _check_face_in_mini_temp(self, image):
        minified_image = image.resize((200, 200))
        with tempfile.NamedTemporaryFile(delete=True, suffix='.jpg') as temp_file:
            minified_image.save(temp_file, format="JPEG")
            is_face_detected = check_face(temp_file.name)
        return is_face_detected
