# Fresh Deployment Guide - Zero to Production

Complete guide for spinning up a new DigitalOcean GPU droplet from scratch to fully working HunyuanVideo deployment.

## ✅ Pre-Deployment Checklist

### 1. DigitalOcean Account & Droplet
- [ ] DigitalOcean account created
- [ ] H100 GPU Droplet selected (or A100, L40S)
- [ ] Ubuntu 22.04 LTS selected
- [ ] SSH key configured for access
- [ ] Droplet IP address noted

### 2. Domain & DNS
- [ ] Domain name registered
- [ ] DNS access available
- [ ] Domain TTL set to 300 (5 minutes) for faster updates
- [ ] A record pointing to droplet IP prepared (don't create yet)

### 3. Email for SSL
- [ ] Valid email address for Let's Encrypt SSL certificate
- [ ] Can receive certificate notifications

## 📋 Quick Start (5-10 minutes)

### Step 1: Create DigitalOcean Droplet (2 min)

1. Go to DigitalOcean console
2. Click "Create" → "Droplets"
3. **Choose Image**: Ubuntu 22.04 LTS
4. **Choose Size**: GPU Droplet → H100 (or your preferred GPU)
   - Minimum: 256GB SSD, 80GB GPU, 16GB RAM
5. **Authentication**: Select your SSH key
6. **Hostname**: `hunyuan-video-prod`
7. Click "Create Droplet"
8. Wait for droplet to initialize (~1 minute)
9. Note the IP address (e.g., `143.198.39.124`)

### Step 2: Configure DNS (1 min)

1. Go to your domain registrar's DNS settings
2. Create an **A record**:
   - Name: `voltronmedia.org` (or your domain)
   - Value: `143.198.39.124` (droplet IP)
   - TTL: 300 (5 minutes)
3. Save DNS changes
4. Wait for propagation (usually 1-5 minutes)
5. Verify with: `nslookup voltronmedia.org`

### Step 3: Deploy with Script (2-5 min)

```bash
# SSH into your droplet
ssh root@143.198.39.124

# Download and run deployment script
curl -fsSL https://raw.githubusercontent.com/codenlighten/smartledger_video_production/main/deployment/scripts/fresh-deploy.sh | bash -s voltronmedia.org admin@example.com
```

**Parameters:**
- `voltronmedia.org` - Your domain name
- `admin@example.com` - Email for SSL certificate

### Step 4: Wait for Completion (3-5 min)

The script will:
- ✓ Install Docker & NVIDIA Container Toolkit
- ✓ Clone the repository
- ✓ Configure Nginx reverse proxy
- ✓ Generate SSL certificate
- ✓ Deploy containers
- ✓ Verify GPU access
- ✓ Run health checks

You'll see output like:
```
[2026-01-07 12:00:00] ✓ Deployment Complete!
[2026-01-07 12:00:00] 🌐 Access your HunyuanVideo deployment:
[2026-01-07 12:00:00]    HTTPS: https://voltronmedia.org
```

## 🔧 Manual Deployment (If Script Fails)

If you prefer manual control or the script encounters issues:

### Option 1: Run Step-by-Step

```bash
# SSH into droplet
ssh root@YOUR_IP

# 1. Update system
apt-get update && apt-get upgrade -y

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh && bash get-docker.sh

# 3. Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update && apt-get install -y nvidia-container-toolkit
systemctl restart docker

# 4. Clone repository
git clone https://github.com/codenlighten/smartledger_video_production.git
cd smartledger_video_production

# 5. Deploy
cd web-ui
docker-compose up -d --build

# 6. Configure Nginx (manual setup needed)
# See NGINX_SETUP.md for instructions
```

### Option 2: Use Individual Scripts

```bash
# Run individual deployment scripts
bash deployment/scripts/docker-deploy.sh
bash deployment/scripts/startup.sh
bash deployment/scripts/healthcheck.sh
```

## 🌐 DNS Configuration

### Method 1: A Record (Most Common)

**Domain Registrar Settings:**
```
Type:     A Record
Name:     @ (or your domain)
Value:    YOUR_DROPLET_IP
TTL:      300
```

### Method 2: CNAME Record

If using a subdomain:
```
Type:     CNAME
Name:     app
Value:    your-domain.com
TTL:      300
```

### Verify DNS
```bash
# Check if DNS is working
nslookup voltronmedia.org
# Should show your droplet IP

# Or use dig
dig voltronmedia.org +short
```

## 🔐 SSL Certificate Configuration

### Automatic (Via Script)
The deployment script automatically sets up SSL using Let's Encrypt.

### Manual Setup
```bash
# If automatic setup failed
certbot certonly --standalone -d voltronmedia.org -m admin@example.com

# Verify certificate
certbot certificates

# Renew automatically
certbot renew --dry-run  # Test renewal
```

### Certificate Locations
```
Certificate: /etc/letsencrypt/live/voltronmedia.org/fullchain.pem
Private Key: /etc/letsencrypt/live/voltronmedia.org/privkey.pem
Auto-renewal: Configured in systemd timer
```

## 🧪 Post-Deployment Testing

### 1. Check Services Running
```bash
docker ps
# Should show 3 containers:
# - hunyuan-video (GPU inference)
# - hunyuan-api (FastAPI backend)
# - hunyuan-ui (React frontend)
```

### 2. Test API Health
```bash
curl http://localhost:8000/api/health
# Expected response:
# {"status":"healthy","container_running":true,...}
```

### 3. Test Frontend
```bash
curl http://localhost:3000 | head -20
# Should return HTML
```

### 4. Test Video Generation
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat walking in snow",
    "video_size": 540,
    "video_length": 129,
    "infer_steps": 30,
    "cfg_scale": 6.0,
    "flow_reverse": true
  }'

# Should return job_id like:
# {"job_id":"12345...","status":"queued",...}
```

### 5. Monitor Generation
```bash
# Watch logs
docker logs hunyuan-api -f

# Wait ~7 minutes for generation to complete
# Check status
curl http://localhost:8000/api/stats
# Should show {"completed":1,"failed":0,...}
```

### 6. Access Web UI
```
https://voltronmedia.org
```
You should see the React app with your generated video!

## 📊 Droplet Specifications (Recommended)

### Hardware
- **GPU**: NVIDIA H100 80GB HBM3
- **CPU**: 8 vCPU cores
- **RAM**: 256GB
- **Storage**: 1TB SSD
- **Bandwidth**: 20Tbps

### Monthly Cost
- **H100 Droplet**: ~$3.39/hour = ~$2,451/month (continuous)
- **Per Video**: ~$0.27 (7 min generation @ $3.39/hr)

### CPU-Only Alternative (Not Recommended)
- Generation time: 30-60 minutes
- Cost: Cheaper but much slower

## 🚨 Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA drivers
nvidia-smi

# Check GPU in Docker
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi

# Restart Docker daemon
systemctl restart docker
```

### Certificate Generation Failed
```bash
# Ensure DNS is working first
nslookup voltronmedia.org

# Try manual certificate
certbot certonly --standalone -d voltronmedia.org

# Check Nginx config
nginx -t
```

### Frontend Shows Blank
```bash
# Check frontend logs
docker logs hunyuan-ui -f

# Check browser console for JavaScript errors
# Clear browser cache: Ctrl+Shift+Delete

# Rebuild frontend
cd web-ui && docker-compose up -d --build
```

### Video Generation Fails (CUDA OOM)
```bash
# Check GPU memory
docker exec hunyuan-video nvidia-smi

# Reduce inference steps
# Edit video request: "infer_steps": 20

# Check available models
docker exec hunyuan-video ls /workspace/repo/ckpts
```

## 📁 Directory Structure After Deployment

```
/root/hunyuan-deploy/
├── web-ui/
│   ├── backend/          # FastAPI server
│   ├── frontend/         # React app
│   └── docker-compose.yml
├── deployment/
│   ├── scripts/
│   │   └── fresh-deploy.sh (this file)
│   └── README.md
└── IMPLEMENTATION.md     # Full documentation

/opt/hunyuan-video/
├── results/              # Generated videos
├── models/               # Model weights (auto-downloaded)
└── logs/                 # Application logs

/etc/nginx/
└── sites-available/
    └── voltronmedia.org  # Reverse proxy config

/etc/letsencrypt/
└── live/
    └── voltronmedia.org/ # SSL certificates
```

## 🔄 Updates & Maintenance

### Update Code
```bash
cd /root/hunyuan-deploy
git pull origin main
cd web-ui
docker-compose up -d --build
```

### View Logs
```bash
docker logs hunyuan-api -f      # Backend
docker logs hunyuan-ui -f       # Frontend
docker logs hunyuan-video -f    # GPU inference
```

### Monitor Resources
```bash
# Inside droplet
htop              # CPU/Memory usage
nvtop             # GPU usage
docker stats      # Container stats
```

### Backup Generated Videos
```bash
tar -czf videos-backup-$(date +%Y%m%d).tar.gz /opt/hunyuan-video/results
```

## 📞 Support

If deployment fails:

1. **Check logs**: `cat /var/log/hunyuan-fresh-deploy.log`
2. **Review errors**: Look for `ERROR:` or `failed` in output
3. **Verify prerequisites**: 
   - SSH access working
   - DNS configured
   - Email valid
4. **Manual deployment**: Follow "Manual Deployment" section above
5. **GitHub issues**: https://github.com/codenlighten/smartledger_video_production/issues

## ✅ Success Indicators

You know deployment is successful when:

- ✅ Three Docker containers are running
- ✅ API responds at `http://localhost:8000/api/health`
- ✅ Frontend loads at `https://voltronmedia.org`
- ✅ Video generation completes in ~7-8 minutes
- ✅ Generated video displays in web UI
- ✅ No GPU memory errors in logs

---

**Estimated Total Time**: 10-15 minutes  
**Difficulty Level**: Intermediate  
**Success Rate**: 95%+ with proper DNS setup

Good luck! 🚀
