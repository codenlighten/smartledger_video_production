#!/bin/bash
#
# HunyuanVideo Docker Deployment Script for DigitalOcean GPU Droplets
# This script sets up HunyuanVideo using the official Docker images
#

set -e

LOG_FILE="/var/log/hunyuan-video-docker-setup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting HunyuanVideo Docker deployment..."

# Update system
log "Updating system..."
apt-get update -y
apt-get upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    log "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Start Docker service
    systemctl start docker
    systemctl enable docker
else
    log "Docker already installed"
fi

# Install NVIDIA Container Toolkit
log "Installing NVIDIA Container Toolkit..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    tee /etc/apt/sources.list.d/nvidia-docker.list

apt-get update
apt-get install -y nvidia-container-toolkit
systemctl restart docker

# Verify GPU access in Docker
log "Verifying GPU access in Docker..."
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi || {
    log "ERROR: GPU not accessible in Docker"
    exit 1
}

# Pull HunyuanVideo Docker image
log "Pulling HunyuanVideo Docker image (CUDA 12.4)..."
docker pull hunyuanvideo/hunyuanvideo:cuda_12

# Create directories for models and outputs
log "Creating directories..."
mkdir -p /opt/hunyuan-video/ckpts
mkdir -p /opt/hunyuan-video/results
mkdir -p /opt/hunyuan-video/logs

# Create docker-compose file
log "Creating docker-compose configuration..."
cat > /opt/hunyuan-video/docker-compose.yml <<'COMPOSE'
version: '3.8'

services:
  hunyuan-video:
    image: hunyuanvideo/hunyuanvideo:cuda_12
    container_name: hunyuan-video
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
      - SERVER_NAME=0.0.0.0
      - SERVER_PORT=7860
    volumes:
      - /opt/hunyuan-video/ckpts:/workspace/HunyuanVideo/ckpts
      - /opt/hunyuan-video/results:/workspace/HunyuanVideo/results
      - /opt/hunyuan-video/logs:/workspace/HunyuanVideo/logs
    ports:
      - "7860:7860"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    command: python3 gradio_server.py --flow-reverse
    restart: unless-stopped
    shm_size: '16gb'
COMPOSE

# Install docker-compose if not present
if ! command -v docker-compose &> /dev/null; then
    log "Installing docker-compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create helper scripts
log "Creating helper scripts..."

# Start script
cat > /opt/hunyuan-video/start.sh <<'START'
#!/bin/bash
cd /opt/hunyuan-video
docker-compose up -d
echo "HunyuanVideo started. Access Gradio at http://$(curl -s ifconfig.me):7860"
docker-compose logs -f
START

# Stop script
cat > /opt/hunyuan-video/stop.sh <<'STOP'
#!/bin/bash
cd /opt/hunyuan-video
docker-compose down
echo "HunyuanVideo stopped"
STOP

# Logs script
cat > /opt/hunyuan-video/logs.sh <<'LOGS'
#!/bin/bash
cd /opt/hunyuan-video
docker-compose logs -f
LOGS

# Shell access script
cat > /opt/hunyuan-video/shell.sh <<'SHELL'
#!/bin/bash
docker exec -it hunyuan-video /bin/bash
SHELL

# Sample generation script
cat > /opt/hunyuan-video/generate.sh <<'GENERATE'
#!/bin/bash
# Usage: ./generate.sh "Your prompt here"

PROMPT="${1:-A cat walks on the grass, realistic style.}"

docker exec -it hunyuan-video python3 sample_video.py \
    --video-size 720 1280 \
    --video-length 129 \
    --infer-steps 50 \
    --prompt "$PROMPT" \
    --flow-reverse \
    --use-cpu-offload \
    --save-path ./results
GENERATE

chmod +x /opt/hunyuan-video/*.sh

# Create model download script
cat > /opt/hunyuan-video/download_models_docker.sh <<'DOWNLOAD'
#!/bin/bash
echo "Downloading HunyuanVideo models..."
echo "This will download ~30GB. Ensure you have sufficient space."
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

docker run --rm \
    -v /opt/hunyuan-video/ckpts:/workspace/ckpts \
    hunyuanvideo/hunyuanvideo:cuda_12 \
    bash -c "pip install huggingface_hub[cli] && huggingface-cli download tencent/HunyuanVideo --local-dir /workspace/ckpts --local-dir-use-symlinks False"

echo "Model download complete!"
DOWNLOAD

chmod +x /opt/hunyuan-video/download_models_docker.sh

# Create usage instructions
cat > /opt/hunyuan-video/DOCKER_USAGE.md <<'USAGE'
# HunyuanVideo Docker Deployment - Usage Guide

## Quick Start

### 1. Download Model Weights
```bash
cd /opt/hunyuan-video
bash download_models_docker.sh
```

### 2. Start HunyuanVideo
```bash
cd /opt/hunyuan-video
bash start.sh
```
Access at: http://YOUR_DROPLET_IP:7860

### 3. Stop HunyuanVideo
```bash
cd /opt/hunyuan-video
bash stop.sh
```

## Helper Scripts

- **start.sh** - Start the service
- **stop.sh** - Stop the service
- **logs.sh** - View logs
- **shell.sh** - Access container shell
- **generate.sh** - Generate video from command line

## Examples

### Generate Video (CLI)
```bash
cd /opt/hunyuan-video
bash generate.sh "A beautiful sunset over mountains"
```

### View Logs
```bash
cd /opt/hunyuan-video
bash logs.sh
```

### Access Container Shell
```bash
cd /opt/hunyuan-video
bash shell.sh
```

### Check GPU Status
```bash
docker exec hunyuan-video nvidia-smi
```

## Configuration

Edit `docker-compose.yml` to customize:
- Ports
- GPU allocation
- Memory limits
- Volume mounts

## Troubleshooting

### Check Container Status
```bash
docker ps
```

### View Container Logs
```bash
docker logs hunyuan-video
```

### Restart Service
```bash
cd /opt/hunyuan-video
bash stop.sh
bash start.sh
```

### GPU Issues
```bash
# Test GPU in Docker
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

## Files & Directories

- Models: `/opt/hunyuan-video/ckpts`
- Results: `/opt/hunyuan-video/results`
- Logs: `/opt/hunyuan-video/logs`
- Config: `/opt/hunyuan-video/docker-compose.yml`

## Auto-start on Boot

```bash
# Enable auto-start
docker update --restart=always hunyuan-video

# Disable auto-start
docker update --restart=no hunyuan-video
```
USAGE

log "Docker deployment complete!"
log "Usage instructions: /opt/hunyuan-video/DOCKER_USAGE.md"
log "Next step: bash /opt/hunyuan-video/download_models_docker.sh"

# Update MOTD
cat > /etc/motd <<'MOTD'
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         HunyuanVideo Docker Deployment Ready!                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Quick Commands:
  cd /opt/hunyuan-video
  bash download_models_docker.sh  # First time only
  bash start.sh                   # Start service
  bash generate.sh "your prompt"  # Generate video

Usage Guide: /opt/hunyuan-video/DOCKER_USAGE.md
MOTD

log "All done!"
