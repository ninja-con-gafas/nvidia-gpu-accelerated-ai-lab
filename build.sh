#!/bin/bash

if [ ! -f .env ]; then
    echo ".env file not found. Using default values."
else
    export $(grep -v '^#' .env | xargs)
fi

$TAG=${TAG:-ninjacongafas/nvidia-gpu-accelerated-ai-lab:latest}

BUILD_ARGS=""
if [ -f .env ]; then
    while IFS='=' read -r key value || [ -n "$key" ]; do
        [[ "$key" =~ ^\s*# ]] && continue
        [[ -z "$key" ]] && continue
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        BUILD_ARGS+="--build-arg ${key}=${value} "
    done < .env
fi

if command -v podman >/dev/null 2>&1; then
    CONTAINER_CMD="podman"
elif command -v docker >/dev/null 2>&1; then
    CONTAINER_CMD="docker"
else
    echo "Error: Neither Podman nor Docker is installed."
    exit 1
fi

$CONTAINER_CMD build $BUILD_ARGS -t "$TAG" .
