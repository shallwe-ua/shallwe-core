from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from PIL import Image
import tempfile

from .facecheck import check_face


class FaceDetectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        uploaded_image = request.data.get('image')
        if uploaded_image:
            is_face_detected = self.check_in_temp(uploaded_image)
            return Response({'is_face_detected': is_face_detected})
        else:
            return Response({'error': 'No image provided'}, status=400)

    def check_in_temp(self, uploaded_image):
        image = Image.open(uploaded_image)
        with tempfile.NamedTemporaryFile(delete=True, suffix='.jpg') as temp_file:
            image.save(temp_file, format="JPEG")
            temp_file_path = temp_file.name
            is_face_detected = check_face(temp_file_path)
        return is_face_detected
