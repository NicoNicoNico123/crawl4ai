#!/bin/bash

# Set variables
IMAGE_NAME="crawl4ai-jupyter"
CONTAINER_NAME="crawl4ai-jupyter-container"
LOCAL_MOUNT_PATH=$(pwd)  # Change this to your desired local path
CONTAINER_MOUNT_PATH="/workspace"
JUPYTER_PORT=8888

# Print script start
echo "Starting Crawl4AI with JupyterLab setup script..."

# Build the Docker image
echo "Building Docker image: $IMAGE_NAME"
docker build --platform linux/amd64 -t $IMAGE_NAME . --progress=plain

# Check if the build was successful
if [ $? -eq 0 ]; then
    echo "Docker image built successfully."
else
    echo "Error: Docker image build failed. Exiting."
    exit 1
fi

# Check if a container with the same name is already running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Container $CONTAINER_NAME is already running. Stopping and removing it."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Run the Docker container
echo "Starting Docker container: $CONTAINER_NAME"
docker run -d \
    --name $CONTAINER_NAME \
    -p $JUPYTER_PORT:8888 \
    -v $LOCAL_MOUNT_PATH:$CONTAINER_MOUNT_PATH \
    $IMAGE_NAME

# Check if the container started successfully
if [ $? -eq 0 ]; then
    echo "Container started successfully."
    
    # Wait for JupyterLab to start (adjust sleep time if needed)
    echo "Waiting for JupyterLab to start..."
    sleep 5
    
    # Get the JupyterLab URL with token
    JUPYTER_URL=$(docker logs $CONTAINER_NAME 2>&1 | grep -o "http://127.0.0.1:8888/lab?token=[a-z0-9]*" | tail -n 1)
    
    if [ -n "$JUPYTER_URL" ]; then
        echo "JupyterLab is running. Access it at:"
        echo "$JUPYTER_URL"
    else
        echo "Couldn't retrieve JupyterLab URL. Check container logs for more information."
    fi
else
    echo "Error: Failed to start the container. Exiting."
    exit 1
fi

echo "Setup complete!"