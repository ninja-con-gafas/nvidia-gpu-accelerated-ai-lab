#!/bin/bash
set -e

if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create one before building."
    exit 1
else
    if command -v podman >/dev/null 2>&1; then
        CONTAINER_CMD="podman"
    elif command -v docker >/dev/null 2>&1; then
        CONTAINER_CMD="docker"
    else
        echo "Error: Neither Docker nor Podman is installed."
        exit 1
    fi
    
    set -a;
    source .env;
    set +a

    for var in BASE_IMAGE_TAG IMAGE_NAME; do
        if [ -z "${!var}" ]; then
            echo "Error: $var is not set in .env file."
            exit 1
        fi
    done

    if [[ "$IMAGE_NAME" == *:* ]]; then
        echo "Error: Do not specify any tag in the IMAGE_NAME"
        exit 1
    fi

    for PACK in $(echo "$PACKS" | tr "," " "); do
        if [ ! -d "packs/$PACK" ]; then
            echo "Error: Pack '$PACK' is not defined."
            echo "Available packs are:"
            echo "$(ls -1 packs)"
            exit 1
        fi
    done
fi

$CONTAINER_CMD build -f Containerfile \
    --build-arg BASE_IMAGE_TAG="$BASE_IMAGE_TAG" \
    -t "${IMAGE_NAME}:base" .

if [ -n "${PACKS:-}" ]; then
    SORTED_PACKS=$(echo "$PACKS" | tr "," " " | tr " " "\n" | sort | tr "\n" " ")
    CURRENT_TAG="${IMAGE_NAME}:base"
    for PACK in $SORTED_PACKS; do
        IMAGE_NAME=${IMAGE_NAME}_${PACK}
        TAG="$IMAGE_NAME:cache"
        $CONTAINER_CMD build -f "packs/$PACK/Containerfile.pack" \
            --build-arg BASE_IMAGE_TAG="$CURRENT_TAG" \
            -t "$TAG" .
        CURRENT_TAG="$TAG"
    done
    $CONTAINER_CMD tag "$CURRENT_TAG" "$IMAGE_NAME:latest"
fi