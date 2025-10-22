import os
import tempfile
from contextlib import redirect_stdout

import cv2
from PIL import Image
from deepface import DeepFace
from django.conf import settings


def _run_backend_silent(image_path, backend):
    try:
        with open(os.devnull, 'w') as null_file:
            with redirect_stdout(null_file):  # redirecting stdout to null to prevent progress bars in console
                result = DeepFace.extract_faces(
                    image_path,
                    detector_backend=backend,
                    enforce_detection=False
                )
                return result
    except cv2.error as e:
        # Catch the bogus crop case that happens in ssd for big face frames and return no faces instead of crashing
        print(f"OpenCV face detector failed for {backend}: {e}")
        return [{'confidence': 0}]


def check_face(image_path):
    backends = settings.SHALLWE_BACKEND_DEEPFACE_MODELS

    results = []
    for backend in backends:
        result = _run_backend_silent(image_path, backend)
        results.append(result)

    is_face_detected = all(result[0]['confidence'] > 0.95 for result in results)
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
    from shallwe_util.efficiency import time_measure, ram_measure

    check_face = time_measure(check_face)
    _run_backend_silent = ram_measure(_run_backend_silent)
