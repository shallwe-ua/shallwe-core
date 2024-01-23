from django.conf import settings
from rest_framework import status

from shallwe_util.tests import AuthorizedAPITestCase


class FaceDetectionViewTest(AuthorizedAPITestCase):

    def _get_response_shortcut(self, image_path: str = None):
        url = 'facecheck'
        method = 'post'

        if image_path:
            from django.contrib.staticfiles import finders
            full_path = finders.find('shallwe_photo/img/' + image_path)
            with open(full_path, 'rb') as image_file:
                response = self._get_response(url, method=method, data={'image': image_file})
        else:
            response = self._get_response(url, method=method)
        return response

    def test_face_detection_no_image(self):
        response = self._get_response_shortcut()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No image provided', response.data['error'])

    def test_face_detection_not_an_image(self):
        response = self._get_response_shortcut('non-image.txt')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Not an image', response.data['error'])

    def test_face_detection_valid_formats(self):
        # Test with various valid image formats
        valid_formats = settings.ALLOWED_PHOTO_FORMATS
        for format_ in valid_formats:
            image_path = f'valid-format.{format_}'
            response = self._get_response_shortcut(image_path)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('success', response.data)
            self.assertTrue(response.data['success'])

    def test_face_detection_valid_rgba(self):
        image_path = f'valid-format-rgba.png'
        response = self._get_response_shortcut(image_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])

    def test_face_detection_invalid_formats(self):
        # Test with various invalid image formats
        invalid_formats = ['bmp', 'gif', 'tiff']
        for format_ in invalid_formats:
            image_path = f'invalid-format.{format_}'
            response = self._get_response_shortcut(image_path)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)
            self.assertIn('Invalid image format', response.data['error'])

    def test_face_detection_too_large_image_size(self):
        # Provide an image larger than the maximum allowed size (e.g., 30MB)
        response = self._get_response_shortcut('large-image-size.jpg')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('File size exceeds the maximum allowed size', response.data['error'])

    def test_face_detection_image_dimensions_too_small(self):
        # Provide an image with dimensions smaller than the minimum allowed size
        response = self._get_response_shortcut('small-dimensions.jpg')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Image dimensions should be at least', response.data['error'])

    def test_face_detection_image_dimensions_too_large(self):
        # Provide an image with dimensions larger than the maximum allowed size
        response = self._get_response_shortcut('large-dimensions.jpg')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Image dimensions exceed the maximum allowed size', response.data['error'])

    def test_face_detection_non_square_image(self):
        # Provide a non-square image
        response = self._get_response_shortcut('non-square.jpg')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Image must be a square', response.data['error'])

    def test_face_detection_no_face(self):
        response = self._get_response_shortcut('flower.jpg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertFalse(response.data['success'])

    def test_face_detection_cat_face(self):
        response = self._get_response_shortcut('cat-face.jpg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertFalse(response.data['success'])

    def test_face_detection_emoji_face(self):
        response = self._get_response_shortcut('emoji-face.jpg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertFalse(response.data['success'])

    def test_face_detection_ok_male_face(self):
        response = self._get_response_shortcut('male-face-anfas.jpg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])

    def test_face_detection_ok_female_face(self):
        response = self._get_response_shortcut('female-face-anfas.jpg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
