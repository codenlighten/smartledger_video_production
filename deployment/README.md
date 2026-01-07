# HunyuanVideo Deployment on DigitalOcean GPU Droplets

This folder provides automation to deploy Tencent HunyuanVideo on DigitalOcean GPU Droplets (H100). You can choose:
- **Manual VM setup** (startup script) 
- **Docker-based deployment**
- **API-driven provisioning** (DigitalOcean API)

## Contents

### Scripts
- `scripts/startup.sh` — Bootstrap on first boot (conda + PyTorch + FlashAttention + xDiT + systemd Gradio)
- `scripts/docker-deploy.sh` — Dockerized deployment with docker-compose
- `scripts/do_api_deploy.py` — Create/delete/list GPU droplets via DigitalOcean API
- `scripts/healthcheck.sh` — Basic liveness check for Gradio + GPU
- `scripts/monitor.sh` — Lightweight periodic GPU/process logging

### Configuration
- `configs/hunyuan.env` — Reusable env defaults for generation/Gradio

### Documentation
- `GPU_SELECTION_GUIDE.md` — Detailed GPU comparison and recommendations
- `COST_COMPARISON.md` — Cost analysis vs Veo 3 and other cloud APIs
- `USE_CASES.md` — Business applications and monetization strategies
- `FEATURE_FILM_PRODUCTION.md` — 90-minute movie production cost analysis and workflow

## Quick Paths
- Manual VM: Use `scripts/startup.sh` as cloud-init/user-data
- Docker: Run `scripts/docker-deploy.sh` on a fresh droplet
- API: `python scripts/do_api_deploy.py create --name my-hy --gpu h100-1x --deployment docker`

## Prerequisites
- DigitalOcean GPU Droplet:
  - **RECOMMENDED: H200 (141GB VRAM, $3.44/hr)** - Best value, 75% more VRAM than H100 for only $0.05 more
  - Budget: H100 (80GB VRAM, $3.39/hr) - Minimum viable
  - Production: H200 x8 or H100 x8 for parallel inference
  - ⚠️ L40S/RTX 6000 (48GB) - Below minimum requirements, expect OOM errors
- SSH key added to your DO account
- API token (for API workflow): export DIGITALOCEAN_TOKEN=... 

## Manual VM Setup (startup.sh)
1) In the DO control panel, create GPU Droplet and paste `scripts/startup.sh` into “Startup scripts”.
2) After boot, SSH and watch: `tail -f /var/log/hunyuan-video-setup.log`.
3) Download models (mandatory):
   ```bash
   cd /opt/hunyuan-video
   bash download_models.sh
   ```
4) Run sample:
   ```bash
   source /opt/miniconda3/bin/activate HunyuanVideo
   python3 sample_video.py \
     --video-size 720 1280 \
     --video-length 129 \
     --infer-steps 50 \
     --prompt "A cat walks on the grass, realistic style." \
     --flow-reverse \
     --use-cpu-offload \
     --save-path ./results
   ```
5) Gradio: `python3 gradio_server.py --flow-reverse` or `systemctl start hunyuan-video` (port 7860).

## Docker Workflow (docker-deploy.sh)
```bash
# On a fresh droplet, copy and run the script
wget https://raw.githubusercontent.com/yourrepo/deployment/scripts/docker-deploy.sh
bash docker-deploy.sh

# Or if you have the repo locally:
bash deployment/scripts/docker-deploy.sh

# After setup completes:
cd /opt/hunyuan-video
bash download_models_docker.sh   # first time only
bash start.sh                    # launches Gradio on 7860
```

**Helper scripts:**
- `stop.sh` - Stop the service
- `logs.sh` - View logs
- `shell.sh` - Access container shell
- `generate.sh "prompt"` - Generate video from CLI

## API Provisioning
```bash
export DIGITALOCEAN_TOKEN=... 

# Recommended: H200 (best value)
python deployment/scripts/do_api_deploy.py create \
  --name hunyuan-h200 \
  --gpu h200-1x \
  --deployment docker \
  --region tor1

# Budget: H100
python deployment/scripts/do_api_deploy.py create \
  --name hunyuan-h100 \
  --gpu h100-1x \
  --deployment docker \
  --region tor1
```
Other commands: `list`, `info`, `delete --name NAME`.

### GPU Options
| GPU | VRAM | Cost | Status |
|-----|------|------|--------|
| **H200** | 141GB | $3.44/hr | ✅ **Recommended** |
| H100 | 80GB | $3.39/hr | ✅ Budget option |
| H200 x8 | 1.1TB | $27.52/hr | ✅ Production |
| H100 x8 | 640GB | $23.92/hr | ✅ Production |
| L40S | 48GB | $1.57/hr | ⚠️ Below minimum |

## Monitoring & Health
- Health: `deployment/scripts/healthcheck.sh` (expects Gradio on :7860)
- Monitor: `deployment/scripts/monitor.sh 30` (interval seconds)

## Notes
- Models (~30GB) are not auto-downloaded; run the download script once.
- Costs: H200 $3.44/hr, H100 $3.39/hr, H200 x8 $27.52/hr, H100 x8 $23.92/hr. Stop/destroy when idle.
- **H200 recommended:** Only $0.05/hr more than H100 but 75% more VRAM (141GB vs 80GB).
- Security: Restrict port 7860, use SSH keys, consider HTTPS via reverse proxy if public.

## Troubleshooting
- GPU in Docker: `docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi`
- Setup logs: `/var/log/hunyuan-video-setup.log` (manual) or `/var/log/hunyuan-video-docker-setup.log` (Docker)
- Service logs: `/var/log/hunyuan-video-server*.log` (systemd) or `docker-compose logs`
