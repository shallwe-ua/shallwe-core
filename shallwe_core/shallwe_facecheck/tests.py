from rest_framework import status

from shallwe_util.tests import AuthorizedAPITestCase


class FaceDetectionViewTest(AuthorizedAPITestCase):

    def _get_response_shortcut(self, image_path: str = None):
        url = 'facecheck'
        method = 'post'

        if image_path:
            from django.contrib.staticfiles import finders
            full_path = finders.find('shallwe_facecheck/img/' + image_path)
            with open(full_path, 'rb') as image_file:
                response = self._get_response(url, method=method, data={'image': image_file})
        else:
            response = self._get_response(url, method=method)
        return response

    def test_face_detection_no_image(self):
        response = self._get_response_shortcut()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No image provided', response.data['error'])

    def test_face_detection_no_face(self):
        response = self._get_response_shortcut('flower.jpg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_face_detected', response.data)
        self.assertFalse(response.data['is_face_detected'])

    def test_face_detection_cat_face(self):
        response = self._get_response_shortcut('cat-face.jpg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_face_detected', response.data)
        self.assertFalse(response.data['is_face_detected'])

    def test_face_detection_emoji_face(self):
        response = self._get_response_shortcut('emoji-face.jpg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_face_detected', response.data)
        self.assertFalse(response.data['is_face_detected'])

    def test_face_detection_ok_male_face(self):
        response = self._get_response_shortcut('male-face-anfas.jpg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_face_detected', response.data)
        self.assertTrue(response.data['is_face_detected'])

    def test_face_detection_ok_female_face(self):
        response = self._get_response_shortcut('female-face-anfas.jpg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_face_detected', response.data)
        self.assertTrue(response.data['is_face_detected'])
