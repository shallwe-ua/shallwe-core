"""
The goal of this script is to trigger download of all deepface model backends used later.
Useful for builds to avoid later runtime downloads which may cause network overhead.
"""

# download_deepface_models.py
import os

# Get the backends list from the environment variable
backends_string = os.environ.get("SHALLWE_BACKEND_DEEPFACE_MODELS", "")
print(f"SHALLWE_BACKEND_DEEPFACE_MODELS is set to: '{backends_string}'")

# Exit early if the environment variable is not set or is empty
if not backends_string:
    print("SHALLWE_BACKEND_DEEPFACE_MODELS is not set or is empty. No models will be downloaded.")
    exit(0)

# Parse the comma-separated list of backends
backends_list = [b.strip() for b in backends_string.split(",") if b.strip()]

# Exit early if no valid backends are found
if not backends_list:
    print("No valid backends found in SHALLWE_BACKEND_DEEPFACE_MODELS. No models will be downloaded.")
    exit(0)

# Create the target directory for deepface weights
# Get the standard deepface home directory
# Assuming it uses the default ~/.deepface. If you use DEEPFACE_HOME env var elsewhere,
# you might need to read that too, but the default location is usually fine for the build.
deepface_home = os.path.join(os.path.expanduser("~"), ".deepface")
weights_dir = os.path.join(deepface_home, "weights")

# Create the directory (and any necessary parent directories) if it doesn't exist
try:
    os.makedirs(weights_dir, exist_ok=True)
    print(f"Ensured directory exists: {weights_dir}")
except Exception as e:
    print(f"Error creating directory {weights_dir}: {e}")
    raise

# Import the FaceDetector class
try:
    from deepface.detectors import FaceDetector
    print("Successfully imported deepface.detectors.FaceDetector.")
except ImportError as e:
    print(f"Error importing deepface.detectors.FaceDetector: {e}")
    raise

# Download models for each specified backend
for backend_name in backends_list:
    print(f"Initializing '{backend_name}' backend to trigger download...")
    try:
        FaceDetector.build_model(backend_name)
        print(f"'{backend_name}' backend initialized and model downloaded (or already present).")
    except Exception as e:
        print(f"Failed to download or initialize model for '{backend_name}': {e}")
        raise

print("Model download script finished successfully.")
