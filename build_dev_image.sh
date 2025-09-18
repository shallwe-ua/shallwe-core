#!/usr/bin/env bash

# This script builds WIP Docker images locally and conveniently updates the variables concerned.
# Attention: It does not push images to the registry, and don't do that with WIPs! Use CI and correct Git tags.

# Check if service argument is provided (read this for usage instruction as well)
if [ $# -eq 0 ]; then
    echo "Usage: $0 <service> [--cleanup N]"
    echo "Services: f (frontend), b (backend), n (nginx)"
    echo "Options: --cleanup N (keep only N most recent images of this service, default=5)"
    exit 1
fi

SERVICE=$1
SERVICE_NAME=""
IMAGE_NAME=""
CLEANUP=false
KEEP_IMAGES=5

# Check for cleanup flag
if [ "$2" = "--cleanup" ]; then
    CLEANUP=true
    if [ -n "$3" ] && [[ "$3" =~ ^[0-9]+$ ]]; then
        KEEP_IMAGES=$3
    fi
fi

# Set service-specific variables
case $SERVICE in
    f)
        SERVICE_NAME="FRONTEND"
        IMAGE_NAME="mock-frontend"
        SOURCE_PATH="./mock_frontend/shallwe/"
        ;;
    b)
        SERVICE_NAME="BACKEND"
        IMAGE_NAME="backend"
        SOURCE_PATH="./shallwe_core/"
        ;;
    n)
        SERVICE_NAME="NGINX"
        IMAGE_NAME="nginx"
        SOURCE_PATH="./nginx/"
        ;;
    *)
        echo "Invalid service. Use: f (frontend), b (backend), n (nginx)"
        exit 1
        ;;
esac

# Set commit hash for tag and relevant env var name to update
COMMIT_HASH=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%m%d-%H%M%S)    # MMDD-HHMMSS
IMAGE_TAG="${COMMIT_HASH}-${TIMESTAMP}"    # Adding timestamp since not all will be commited right away

ENV_VAR_NAME="SHALLWE_GLOBAL_DOCKER_${SERVICE_NAME}_IMAGE_TAG"

# Read previous tag from .env if exists (for quick revert comment alongside new value)
PREV_TAG=""
if [ -f .env ]; then
    PREV_TAG=$(grep "$ENV_VAR_NAME" .env | cut -d'=' -f2 | cut -d' ' -f1)
fi

# Create the new value line
NEW_VALUE_LINE="$ENV_VAR_NAME=\"$IMAGE_TAG\""
if [ -n "$PREV_TAG" ]; then
    NEW_VALUE_LINE="$NEW_VALUE_LINE    # Previous: $PREV_TAG"  # Add previous tag as side-comment if any
fi

# Update .env file preserving existing content and order
TEMP_FILE=$(mktemp)
LINE_FOUND=false

if [ -f .env ]; then
    while IFS= read -r line || [ -n "$line" ]; do
        if [[ $line == $ENV_VAR_NAME=* ]]; then
            echo "$NEW_VALUE_LINE" >> "$TEMP_FILE"
            LINE_FOUND=true
        elif [[ -n "$line" ]]; then
            echo "$line" >> "$TEMP_FILE"
        fi
    done < .env
fi

# If variable wasn't found (or no .env file), add it
if [ "$LINE_FOUND" = false ]; then
    echo "$NEW_VALUE_LINE" >> "$TEMP_FILE"
fi

mv "$TEMP_FILE" .env

# Build image (don't push)
if [ "$SERVICE" = "b" ]; then
    # For the backend, pass the DeepFace models env var as a build arg
    docker build --build-arg SHALLWE_BACKEND_DEEPFACE_MODELS -t "$IMAGE_NAME:$IMAGE_TAG" "$SOURCE_PATH"
else
    # For other services, build normally
    docker build -t "$IMAGE_NAME:$IMAGE_TAG" "$SOURCE_PATH"
fi
echo "Built locally: $IMAGE_NAME:$IMAGE_TAG from $SOURCE_PATH"
echo "Updated .env with $ENV_VAR_NAME=$IMAGE_TAG"

# Cleanup old images if requested
if [ "$CLEANUP" = true ]; then
    echo "Keeping only $KEEP_IMAGES most recent images for $IMAGE_NAME..."

    # Get list of images for this service, sorted by creation time (newest first)
    OLD_IMAGES=$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}" | \
                grep "^$IMAGE_NAME " | \
                tail -n +$((KEEP_IMAGES + 1)) | \
                awk '{print $2}')

    # Remove old images
    if [ -n "$OLD_IMAGES" ]; then
        echo "Removing old images:"
        echo "$OLD_IMAGES" | while read tag; do
            if [ -n "$tag" ] && [ "$tag" != "<none>" ]; then
                echo "  $IMAGE_NAME:$tag"
                docker rmi "$IMAGE_NAME:$tag" 2>/dev/null || true
            fi
        done
    else
        echo "No old images to remove"
    fi
fi


# -------- Apply env var immediately if possible ---------
# If autoenv is present - try applying
if command -v autoenv_init > /dev/null; then
  if [[ -f .env ]]; then
    echo "📦 Detected .env file, triggering autoenv by re-entering directory...."
    cd .
  else
    echo "⚠️ Autoenv detected but no .env file found."
  fi

# No autoenv – try sourcing .env manually
else
  if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    echo "🪄 Applying .env variables to current shell..."
    echo "Hint: install autoenv to automate this step."
    set -a
    source .env 2>/dev/null && echo "✅ .env loaded." || echo "⚠️ No .env file found."
    set +a
  else
    echo "ℹ️  .env updated. To apply changes: run 'source .env'"
  fi
fi
