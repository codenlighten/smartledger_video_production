# Quick Deployment Checklist

**Time Needed**: 15 minutes  
**Difficulty**: Intermediate

## Pre-Flight Check

- [ ] DigitalOcean account with payment method
- [ ] Domain name registered
- [ ] Valid email address
- [ ] SSH key generated locally
- [ ] Droplet IP address accessible

## Deployment Steps

### 1. Create Droplet (2 min)

```bash
# DigitalOcean Console
1. Click "Create" → "Droplets"
2. Image: Ubuntu 22.04 LTS
3. Size: GPU → H100 (most tested)
4. Auth: Your SSH key
5. Hostname: hunyuan-video-prod
6. Click "Create"
7. Note IP: 143.198.39.124 (example)
```

- [ ] Droplet created
- [ ] IP address noted: _______________

### 2. Configure DNS (1 min)

```bash
# Domain Registrar Console
1. Go to DNS settings
2. Create A Record:
   - Name: voltronmedia.org (your domain)
   - Type: A
   - Value: 143.198.39.124 (your IP)
   - TTL: 300
3. Save changes
4. Wait 1-5 minutes for propagation
```

- [ ] DNS A record created
- [ ] DNS propagation verified: `nslookup yourdomain.com`

### 3. Deploy (3 min)

```bash
# SSH into droplet
ssh root@YOUR_IP

# Download and run deployment script
curl -fsSL https://raw.githubusercontent.com/codenlighten/smartledger_video_production/main/deployment/scripts/fresh-deploy.sh | bash -s yourdomain.com your-email@example.com

# Wait for completion (~3 minutes)
# You'll see: "✓ Deployment Complete!"
```

- [ ] SSH connection established
- [ ] Deployment script running
- [ ] Deployment completed successfully
- [ ] Email: _________________
- [ ] Domain: _________________

### 4. Verify (2 min)

```bash
# Check services
docker ps
# Should show 3 containers

# Check API
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:3000 | head

# Access web UI
https://yourdomain.com
```

- [ ] All 3 Docker containers running
- [ ] API responding (status: "healthy")
- [ ] Frontend loading
- [ ] Web UI accessible

### 5. Test Video Generation (8 min)

```bash
# Submit a test generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A golden sunset over mountains",
    "video_size": 540,
    "infer_steps": 30
  }'

# Monitor progress
watch -n 2 'curl -s http://localhost:8000/api/stats | jq .'

# Check logs
docker logs hunyuan-api -f
```

- [ ] Video generation submitted
- [ ] Progress visible in logs
- [ ] Video generated successfully (~7-8 min)
- [ ] Video visible in web UI

## Success = ✅ All Boxes Checked

When you can:
1. ✅ SSH into droplet
2. ✅ Access web UI at https://yourdomain.com
3. ✅ See 3 running containers
4. ✅ Generate a video in ~7-8 minutes
5. ✅ View video in browser

**You're ready for production!**

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| DNS not resolving | Wait 5 minutes, check registrar settings |
| SSL certificate failed | Ensure DNS is working first, then run certbot |
| GPU not detected | Check nvidia-smi, restart docker |
| Blank frontend | Check docker logs hunyuan-ui, clear browser cache |
| Video generation fails | Check GPU memory, reduce infer_steps |
| Containers won't start | Check: `docker logs hunyuan-api` |

## Important Files & Locations

```
Deployment Script:  /root/hunyuan-deploy/deployment/scripts/fresh-deploy.sh
Configuration:      /root/hunyuan-deploy/web-ui/.env
Docker Compose:     /root/hunyuan-deploy/web-ui/docker-compose.yml
Nginx Config:       /etc/nginx/sites-enabled/yourdomain.com
SSL Certificate:    /etc/letsencrypt/live/yourdomain.com/
Generated Videos:   /opt/hunyuan-video/results/
Logs:              /var/log/hunyuan-fresh-deploy.log
```

## Useful Commands

```bash
# Check container status
docker ps

# View logs
docker logs -f hunyuan-api
docker logs -f hunyuan-ui
docker logs -f hunyuan-video

# Check GPU
docker exec hunyuan-video nvidia-smi

# Check API stats
curl http://localhost:8000/api/stats

# Restart containers
docker-compose -f /root/hunyuan-deploy/web-ui/docker-compose.yml restart

# Update code
cd /root/hunyuan-deploy && git pull && cd web-ui && docker-compose up -d --build
```

## Emergency Commands

```bash
# Stop all containers
docker-compose -f /root/hunyuan-deploy/web-ui/docker-compose.yml down

# Hard restart (if stuck)
docker kill hunyuan-api hunyuan-ui hunyuan-video
docker-compose -f /root/hunyuan-deploy/web-ui/docker-compose.yml up -d

# View deployment log
tail -100 /var/log/hunyuan-fresh-deploy.log

# Check disk space
df -h

# Check memory
free -h

# Clear old Docker images
docker image prune -a
```

## Cost Estimate

| Item | Cost |
|------|------|
| H100 Droplet | $3.39/hour |
| Monthly (24/7) | ~$2,451 |
| Per Video (7 min) | ~$0.27 |
| SSL Certificate | FREE (Let's Encrypt) |

## Support Resources

- **Full Documentation**: `/root/hunyuan-deploy/IMPLEMENTATION.md`
- **Deployment Guide**: `/root/hunyuan-deploy/FRESH_DEPLOYMENT.md`
- **GitHub Repository**: https://github.com/codenlighten/smartledger_video_production
- **API Documentation**: `http://localhost:8000/docs`

---

**Status**: Production Ready  
**Last Updated**: January 7, 2026  
**Tested On**: DigitalOcean H100 GPU Droplet
