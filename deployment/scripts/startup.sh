#!/bin/bash
#
# HunyuanVideo Startup Script for DigitalOcean GPU Droplets
# This script runs on initial droplet boot to set up the environment
#
# Usage: Add this as a startup script in the DigitalOcean GPU Droplet creation
#

set -e

# Configuration
LOG_FILE="/var/log/hunyuan-video-setup.log"
INSTALL_DIR="/opt/hunyuan-video"
CUDA_VERSION="12.4"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting HunyuanVideo setup on DigitalOcean GPU Droplet..."

# Update system
log "Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install required dependencies
log "Installing system dependencies..."
apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    python3-pip \
    python3-dev \
    python3-venv \
    nvidia-cuda-toolkit \
    nvidia-utils-535 \
    ninja-build \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    htop \
    nvtop \
    screen \
    tmux

# Verify NVIDIA GPU
log "Verifying NVIDIA GPU setup..."
nvidia-smi || {
    log "ERROR: NVIDIA GPU not detected. Please check your GPU configuration."
    exit 1
}

# Install Miniconda
log "Installing Miniconda..."
if [ ! -d "/opt/miniconda3" ]; then
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p /opt/miniconda3
    rm /tmp/miniconda.sh
    
    # Add conda to PATH for all users
    echo 'export PATH="/opt/miniconda3/bin:$PATH"' >> /etc/profile.d/conda.sh
    chmod +x /etc/profile.d/conda.sh
fi

export PATH="/opt/miniconda3/bin:$PATH"

# Clone HunyuanVideo repository
log "Cloning HunyuanVideo repository..."
if [ ! -d "$INSTALL_DIR" ]; then
    git clone https://github.com/Tencent-Hunyuan/HunyuanVideo "$INSTALL_DIR"
else
    log "Repository already exists, pulling latest changes..."
    cd "$INSTALL_DIR"
    git pull
fi

cd "$INSTALL_DIR"

# Create conda environment
log "Creating conda environment..."
/opt/miniconda3/bin/conda create -n HunyuanVideo python=3.10.9 -y

# Activate environment and install dependencies
log "Installing PyTorch and dependencies..."
source /opt/miniconda3/bin/activate HunyuanVideo

# Install PyTorch with CUDA 12.4
conda install -y pytorch==2.6.0 torchvision==0.19.0 torchaudio==2.4.0 pytorch-cuda=12.4 -c pytorch -c nvidia

# Install pip dependencies
log "Installing Python packages..."
pip install -r requirements.txt

# Install flash attention
log "Installing Flash Attention v2..."
pip install ninja
pip install git+https://github.com/Dao-AILab/flash-attention.git@v2.6.3

# Install xDiT for multi-GPU support
log "Installing xDiT for parallel inference..."
pip install xfuser==0.4.0

# Fix CUBLAS if needed
log "Installing CUBLAS..."
pip install nvidia-cublas-cu12==12.4.5.8

# Create directories for models and outputs
log "Creating working directories..."
mkdir -p "$INSTALL_DIR/ckpts"
mkdir -p "$INSTALL_DIR/results"
mkdir -p "$INSTALL_DIR/logs"

# Set permissions
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"

# Create systemd service for Gradio server (optional)
log "Creating systemd service..."
cat > /etc/systemd/system/hunyuan-video.service <<EOF
[Unit]
Description=HunyuanVideo Gradio Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=/opt/miniconda3/envs/HunyuanVideo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/miniconda3/envs/HunyuanVideo/bin/python gradio_server.py --flow-reverse
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/hunyuan-video-server.log
StandardError=append:/var/log/hunyuan-video-server-error.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

# Create download script for model weights
log "Creating model download script..."
cat > "$INSTALL_DIR/download_models.sh" <<'DOWNLOAD_SCRIPT'
#!/bin/bash
# Script to download HunyuanVideo model weights
# Run this manually after setup: bash download_models.sh

set -e

echo "Downloading HunyuanVideo model weights..."
echo "This will download approximately 30GB of model files."
echo "Please ensure you have sufficient disk space."
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

cd /opt/hunyuan-video/ckpts

# Install huggingface-cli if not present
pip install huggingface_hub[cli] -q

# Download models
echo "Downloading models from Hugging Face..."
huggingface-cli download tencent/HunyuanVideo --local-dir /opt/hunyuan-video/ckpts --local-dir-use-symlinks False

echo "Model download complete!"
echo "Models are stored in: /opt/hunyuan-video/ckpts"
DOWNLOAD_SCRIPT

chmod +x "$INSTALL_DIR/download_models.sh"

# Create usage instructions
log "Creating usage instructions..."
cat > "$INSTALL_DIR/DIGITALOCEAN_USAGE.md" <<'USAGE'
# HunyuanVideo on DigitalOcean GPU Droplet - Usage Guide

## Setup Complete! Next Steps:

### 1. Download Model Weights
The model weights are not included in the initial setup. Run:
```bash
cd /opt/hunyuan-video
bash download_models.sh
```
This will download ~30GB of model files from Hugging Face.

### 2. Activate Environment
```bash
source /opt/miniconda3/bin/activate HunyuanVideo
cd /opt/hunyuan-video
```

### 3. Test Single Video Generation
```bash
python3 sample_video.py \
    --video-size 720 1280 \
    --video-length 129 \
    --infer-steps 50 \
    --prompt "A cat walks on the grass, realistic style." \
    --flow-reverse \
    --use-cpu-offload \
    --save-path ./results
```

### 4. Start Gradio Web Interface
```bash
# Option 1: Run directly
python3 gradio_server.py --flow-reverse

# Option 2: Use systemd service
systemctl start hunyuan-video
systemctl enable hunyuan-video  # Auto-start on boot

# Check service status
systemctl status hunyuan-video
```

Access the Gradio interface at: http://YOUR_DROPLET_IP:7860

### 5. Multi-GPU Parallel Inference (if using H100 x8)
```bash
torchrun --nproc_per_node=8 sample_video.py \
    --video-size 1280 720 \
    --video-length 129 \
    --infer-steps 50 \
    --prompt "A cat walks on the grass, realistic style." \
    --flow-reverse \
    --seed 42 \
    --ulysses-degree 8 \
    --ring-degree 1 \
    --save-path ./results
```

### 6. Monitor GPU Usage
```bash
# Real-time GPU monitoring
nvidia-smi -l 1

# Or use nvtop for better visualization
nvtop
```

### GPU Configurations:
- **H100 x1 (80GB VRAM)**: Perfect for 720p generation with use-cpu-offload
- **H100 x8 (640GB VRAM)**: Optimal for parallel inference and higher resolution

### Logs:
- Setup log: `/var/log/hunyuan-video-setup.log`
- Server log: `/var/log/hunyuan-video-server.log`
- Error log: `/var/log/hunyuan-video-server-error.log`

### Security Notes:
- Configure firewall rules for port 7860 if using Gradio web interface
- Use SSH keys for authentication
- Consider setting up nginx reverse proxy with SSL for production

### Cost Optimization:
- Stop the Gradio service when not in use: `systemctl stop hunyuan-video`
- Take snapshots of configured droplet for faster re-deployment
- Use DigitalOcean's API to automate start/stop based on usage

For more information, see the main README at:
https://github.com/Tencent-Hunyuan/HunyuanVideo
USAGE

log "Setup complete!"
log "Please read /opt/hunyuan-video/DIGITALOCEAN_USAGE.md for next steps"
log "Key next step: Run 'bash /opt/hunyuan-video/download_models.sh' to download model weights"

# Create a banner for SSH login
cat > /etc/motd <<'MOTD'
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              HunyuanVideo GPU Droplet Ready!                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Setup Status: COMPLETE ✓

Next Steps:
1. Download models: bash /opt/hunyuan-video/download_models.sh
2. Activate env: source /opt/miniconda3/bin/activate HunyuanVideo
3. See usage guide: cat /opt/hunyuan-video/DIGITALOCEAN_USAGE.md

GPU Status:
MOTD

nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader >> /etc/motd

echo "" >> /etc/motd
echo "Installation directory: /opt/hunyuan-video" >> /etc/motd
echo "Setup log: /var/log/hunyuan-video-setup.log" >> /etc/motd
echo "" >> /etc/motd

log "All done! System is ready for HunyuanVideo inference."
