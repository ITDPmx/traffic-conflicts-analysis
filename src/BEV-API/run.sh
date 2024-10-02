#!/bin/bash

echo "Running API"

image_name="birds-eye-view"

if ! docker images --format '{{.Repository}}' | grep -q "$image_name"; then
    echo "Image $image_name doesn't exist, building image..."
    docker build -t birds-eye-view .
else
    echo "image $image_name exists, skipping build"
fi

docker run -d --runtime=nvidia --gpus all  --name bev -p 8000:8000 birds-eye-view
# docker run -it --gpus all --name bev -u $(id -u):$(id -g) --rm -p 8000:8000  -v $(pwd):/app -w /app --env DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix birds-eye-view /bin/bash
