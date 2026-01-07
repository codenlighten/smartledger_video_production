#!/bin/bash

###############################################################################
#                                                                             #
#  HunyuanVideo Web UI - Fresh Droplet Deployment Script                    #
#                                                                             #
#  This script will set up a complete working HunyuanVideo deployment        #
#  on a fresh DigitalOcean GPU droplet from scratch.                         #
#                                                                             #
#  Prerequisites:                                                             #
#  - DigitalOcean H100 GPU Droplet (143GB+ storage, 16GB+ RAM)               #
#  - Ubuntu 22.04 LTS                                                        #
#  - SSH access as root                                                      #
#  - 80GB+ free storage for models                                           #
#                                                                             #
#  Usage: bash fresh-deploy.sh [domain] [email]                             #
#  Example: bash fresh-deploy.sh voltronmedia.org admin@example.com         #
#                                                                             #
###############################################################################

set -e

# Configuration
DOMAIN="${1:-voltronmedia.org}"
EMAIL="${2:-admin@example.com}"
REPO_URL="https://github.com/codenlighten/smartledger_video_production.git"
INSTALL_DIR="/root/hunyuan-deploy"
LOG_FILE="/var/log/hunyuan-fresh-deploy.log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

# Start
log "=========================================="
log "HunyuanVideo Fresh Deployment"
log "=========================================="
log "Domain: $DOMAIN"
log "Email: $EMAIL"
log "Install Directory: $INSTALL_DIR"
log ""

# Step 1: System update
log "Step 1: Updating system packages..."
apt-get update -y > /dev/null 2>&1
apt-get upgrade -y > /dev/null 2>&1
log "✓ System updated"

# Step 2: Install system dependencies
log "Step 2: Installing system dependencies..."
apt-get install -y \
    git curl wget \
    build-essential python3-pip python3-dev \
    docker.io docker-compose \
    nginx certbot python3-certbot-nginx \
    htop nvtop tmux screen \
    ffmpeg > /dev/null 2>&1
log "✓ System dependencies installed"

# Step 3: Enable Docker service
log "Step 3: Configuring Docker..."
systemctl enable docker
systemctl start docker
log "✓ Docker service started"

# Step 4: Install NVIDIA Container Toolkit
log "Step 4: Installing NVIDIA Container Toolkit..."
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    tee /etc/apt/sources.list.d/nvidia-docker.list > /dev/null
apt-get update -y > /dev/null 2>&1
apt-get install -y nvidia-container-toolkit > /dev/null 2>&1
systemctl restart docker
log "✓ NVIDIA Container Toolkit installed"

# Step 5: Verify GPU
log "Step 5: Verifying GPU access..."
if ! docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
    error "GPU not accessible in Docker. Please verify NVIDIA drivers are installed."
fi
log "✓ GPU verified and accessible"

# Step 6: Clone repository
log "Step 6: Cloning repository..."
rm -rf "$INSTALL_DIR"
git clone "$REPO_URL" "$INSTALL_DIR" > /dev/null 2>&1
cd "$INSTALL_DIR"
log "✓ Repository cloned"

# Step 7: Create environment file
log "Step 7: Creating environment configuration..."
cat > web-ui/.env << EOF
# HunyuanVideo Configuration
DOMAIN=$DOMAIN
EMAIL=$EMAIL
ENVIRONMENT=production

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=2

# Frontend Configuration
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=3000

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Storage Configuration
RESULTS_DIR=/opt/hunyuan-video/results
MODELS_DIR=/opt/hunyuan-video/models

# Logging
LOG_LEVEL=info
DEBUG=false
EOF
log "✓ Environment configuration created"

# Step 8: Create necessary directories
log "Step 8: Creating storage directories..."
mkdir -p /opt/hunyuan-video/results
mkdir -p /opt/hunyuan-video/models
chmod -R 755 /opt/hunyuan-video
log "✓ Storage directories created"

# Step 9: Configure Nginx
log "Step 9: Configuring Nginx reverse proxy..."
cat > /etc/nginx/sites-available/$DOMAIN << 'NGINX'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name DOMAIN_PLACEHOLDER;

    ssl_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Disable vite.svg 404 errors
    location = /vite.svg {
        return 204;
    }

    # Frontend (React)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
    }

    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
NGINX

sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /etc/nginx/sites-available/$DOMAIN
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/$DOMAIN
rm -f /etc/nginx/sites-enabled/default
nginx -t > /dev/null 2>&1
systemctl enable nginx
systemctl start nginx
log "✓ Nginx configured"

# Step 10: Get SSL certificate
log "Step 10: Generating SSL certificate..."
log "Note: Make sure DNS is pointing to this server ($DOMAIN -> your IP)"
log "Waiting 30 seconds before certificate generation..."
sleep 30

if ! certbot certonly --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" 2>&1 | grep -q "Successfully received certificate"; then
    warn "SSL certificate generation failed. This may be due to DNS not being configured."
    warn "Configure DNS and run: certbot certonly --nginx -d $DOMAIN"
fi
systemctl reload nginx
log "✓ SSL certificate configured (or will be set up after DNS)"

# Step 11: Deploy Docker containers
log "Step 11: Deploying Docker containers..."
cd "$INSTALL_DIR/web-ui"

# Build and start containers
docker-compose up -d --build > /dev/null 2>&1
log "✓ Containers deployed"

# Step 12: Wait for services to be ready
log "Step 12: Waiting for services to be ready..."
sleep 10

# Check if backend is responding
for i in {1..30}; do
    if curl -s http://localhost:8000/api/stats > /dev/null 2>&1; then
        log "✓ Backend API is responding"
        break
    fi
    if [ $i -eq 30 ]; then
        error "Backend API failed to start after 30 seconds"
    fi
    echo "Attempt $i/30..."
    sleep 1
done

# Check if frontend is responding
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        log "✓ Frontend is responding"
        break
    fi
    if [ $i -eq 30 ]; then
        error "Frontend failed to start after 30 seconds"
    fi
    echo "Attempt $i/30..."
    sleep 1
done

# Step 13: Verify GPU in container
log "Step 13: Verifying GPU in container..."
if docker exec hunyuan-video nvidia-smi > /dev/null 2>&1; then
    log "✓ GPU accessible in container"
else
    warn "GPU may not be accessible in container"
fi

# Step 14: Final status
log ""
log "=========================================="
log "✓ Deployment Complete!"
log "=========================================="
log ""
log "🌐 Access your HunyuanVideo deployment:"
log ""
log "   HTTP:  http://$DOMAIN (redirects to HTTPS)"
log "   HTTPS: https://$DOMAIN"
log "   API:   http://localhost:8000/api/docs"
log ""
log "📊 Next Steps:"
log ""
log "1. Configure DNS to point $DOMAIN to $(hostname -I | awk '{print $1}')"
log "2. If SSL failed, run: certbot certonly --nginx -d $DOMAIN"
log "3. Generate your first video:"
log ""
log "   curl -X POST http://localhost:8000/api/generate \\"
log "     -H 'Content-Type: application/json' \\"
log "     -d '{\"prompt\":\"A cat walking in snow\",\"video_size\":540}'"
log ""
log "4. Monitor logs:"
log "   docker logs hunyuan-api -f"
log "   docker logs hunyuan-ui -f"
log "   docker logs hunyuan-video -f"
log ""
log "5. Check stats:"
log "   curl http://localhost:8000/api/stats"
log ""
log "📝 Configuration file: $INSTALL_DIR/web-ui/.env"
log "📍 Repository: $INSTALL_DIR"
log "🔍 Logs: $LOG_FILE"
log ""
log "=========================================="
log "Enjoy generating videos! 🎬"
log "=========================================="
