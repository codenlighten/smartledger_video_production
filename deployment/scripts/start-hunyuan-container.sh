#!/bin/bash
# Start or restart the HunyuanVideo container with GPU access
# This script ensures the container has proper GPU access for video generation

set -e

CONTAINER_NAME="hunyuan-video"
IMAGE="hunyuanvideo/hunyuanvideo:cuda_12"

echo "🔍 Checking if $CONTAINER_NAME container exists..."

# Stop and remove existing container if it exists
if docker ps -a | grep -q $CONTAINER_NAME; then
    echo "🛑 Stopping existing $CONTAINER_NAME container..."
    docker stop $CONTAINER_NAME || true
    echo "🗑️  Removing existing $CONTAINER_NAME container..."
    docker rm $CONTAINER_NAME || true
fi

echo "🚀 Starting $CONTAINER_NAME container with GPU access..."

docker run -d \
    --gpus all \
    --name $CONTAINER_NAME \
    -v /workspace:/workspace \
    -v /opt/hunyuan-video:/opt/hunyuan-video \
    --restart=unless-stopped \
    $IMAGE \
    /bin/bash -c 'sleep infinity'

echo "✅ Container started successfully!"
echo ""
echo "🧪 Testing GPU access..."

if docker exec $CONTAINER_NAME nvidia-smi > /dev/null 2>&1; then
    echo "✅ GPU is accessible inside the container"
    docker exec $CONTAINER_NAME nvidia-smi | head -20
else
    echo "❌ ERROR: GPU is not accessible. Check NVIDIA driver installation."
    exit 1
fi

echo ""
echo "📊 Container status:"
docker ps | grep $CONTAINER_NAME

echo ""
echo "✅ HunyuanVideo container is ready for video generation!"
