import os
import tempfile
from contextlib import redirect_stdout

from PIL import Image
from deepface import DeepFace
from django.conf import settings

from shallwe_util.efficiency import time_measure


def check_face(image_path):
    backends = ['ssd', 'mtcnn', 'retinaface']

    results = []
    for backend in backends:
        with open(os.devnull, 'w') as null_file:
            with redirect_stdout(null_file):    # redirecting stdout to null to prevent progress bars in console
                results.append(DeepFace.extract_faces(
                    image_path,
                    detector_backend=backend,
                    enforce_detection=False
                ))
    is_face_detected = all(result[0]["confidence"] > 0.95 for result in results)
    return is_face_detected


def check_face_minified_temp(image: Image.Image):
    minified_image = image.resize((200, 200))
    # Get rid of alpha channel
    if minified_image.mode == 'RGBA':
        rgb_image = Image.new('RGB', minified_image.size, (255, 255, 255))
        # Paste the original image onto the new image, using the alpha channel as a mask
        rgb_image.paste(minified_image, mask=minified_image.split()[3])
        minified_image = rgb_image
    # Check in temp jpg file
    with tempfile.NamedTemporaryFile(delete=True, suffix='.jpg') as temp_file:
        minified_image.save(temp_file, format='JPEG')
        is_face_detected = check_face(temp_file.name)
    return is_face_detected


if settings.SHALLWE_GLOBAL_ENV_MODE == 'DEV':
    check_face = time_measure(check_face)
