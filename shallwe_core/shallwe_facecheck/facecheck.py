import os
from contextlib import redirect_stdout

import environ
from deepface import DeepFace

from shallwe_util.efficiency import time_measure

env = environ.Env()
environ.Env.read_env()


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


if env('SHALLWE_BACKEND_MODE') == 'DEV':
    check_face = time_measure(check_face)
