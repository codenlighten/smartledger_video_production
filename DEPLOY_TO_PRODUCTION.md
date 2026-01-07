# Deploy Phase 1 Optimizations to Production

## Server Info
- **IP**: 143.198.39.124
- **Domain**: https://voltronmedia.org
- **GPU**: H100 80GB HBM3

## Pre-Deployment Checklist
✅ Code committed to GitHub (Phase 1 optimizations)
✅ Redis cache integration complete
✅ Adaptive optimizer implemented
✅ Quality tier system ready
✅ Frontend optimization badges added

---

## Deployment Steps

### 1. SSH to Production Server
```bash
ssh root@143.198.39.124
```

### 2. Navigate to Repository
```bash
cd /opt/hunyuan-video/smartledger_video_production
```

### 3. Pull Latest Changes
```bash
git pull origin main
```

### 4. Navigate to Web UI Directory
```bash
cd web-ui
```

### 5. Stop Current Services
```bash
docker-compose down
```

### 6. Rebuild with Optimizations
```bash
docker-compose build --no-cache
```

### 7. Start Services with Redis
```bash
docker-compose up -d
```

### 7.5. Ensure HunyuanVideo Container Has GPU Access
```bash
cd ../deployment/scripts
./start-hunyuan-container.sh
cd ../../web-ui
```

**IMPORTANT**: The HunyuanVideo container must be started with `--gpus all` flag to access the H100 GPU. This script ensures proper GPU access.

### 8. Verify Services are Running
```bash
docker-compose ps
```

You should see 3 services:
- `hunyuan-cache` (Redis)
- `hunyuan-api` (Backend with optimizations)
- `hunyuan-ui` (Frontend)

### 9. Check Backend Logs
```bash
docker-compose logs -f backend
```

Look for:
```
✅ Redis cache connected at redis:6379
🚀 HunyuanVideo API started with optimizations enabled
```

### 10. Test Cache Connection
```bash
docker exec hunyuan-cache redis-cli ping
```

Should return: `PONG`

### 11. Check API Health
```bash
curl http://localhost:8000/api/health
```

### 12. Check Optimization Stats
```bash
curl http://localhost:8000/api/stats | jq '.optimization'
```

Should show:
```json
{
  "cache_enabled": true,
  "cache_hits": 0,
  "cache_hit_rate": 0,
  "avg_steps": 30,
  "adaptive_enabled": true
}
```

### 13. Test Frontend
Open browser to: https://voltronmedia.org

Check for:
- Quality tier selector (Preview/Standard/Premium) in generation form
- New stats cards showing "Cache Hit Rate" and "Avg Steps"
- Optimization badges on video cards (will appear after first generation)

---

## Quick Deployment (One-Liner)

If you're confident, run this after SSHing:

```bash
cd /opt/hunyuan-video/smartledger_video_production && \
git pull origin main && \
cd web-ui && \
docker-compose down && \
docker-compose build --no-cache && \
docker-compose up -d && \
docker-compose logs -f backend
```

Press `Ctrl+C` when you see the startup messages, then test the site.

---

## Testing the Optimizations

### Test 1: Simple Prompt (Should use ~18-20 steps)
```
Prompt: "A cat sitting on a chair"
Quality: Auto
Expected: Simple complexity, ~18 steps, ~3 min
```

### Test 2: Complex Prompt (Should use ~35-40 steps)
```
Prompt: "Cinematic drone shot flying through a crowded city marketplace at sunset with dramatic lighting, people walking, cars moving, intricate details, photorealistic 8k"
Quality: Auto
Expected: Very complex, ~40 steps, ~8 min
```

### Test 3: Cache Hit (Repeat same prompt)
Run Test 1 again - should see "Cache Hit" badge on the video card

### Test 4: Quality Tiers
Try same prompt with:
- **Preview**: ~15 steps, ~2 min
- **Standard**: ~25 steps, ~5 min  
- **Premium**: ~45 steps, ~9 min

---

## Monitoring Commands

### Watch Redis Stats
```bash
docker exec hunyuan-cache redis-cli INFO stats
```

### Monitor Cache Keys
```bash
docker exec hunyuan-cache redis-cli KEYS "embed:*"
```

### View Cache Memory Usage
```bash
docker exec hunyuan-cache redis-cli INFO memory
```

### Backend Logs (Live)
```bash
docker-compose logs -f backend
```

### All Services Logs
```bash
docker-compose logs -f
```

---

## Rollback Plan

If something goes wrong:

### Option 1: Restart Services
```bash
docker-compose restart
```

### Option 2: Full Rollback
```bash
cd /opt/hunyuan-video/smartledger_video_production
git log --oneline  # Note the commit hash before optimizations
git checkout <previous-commit-hash>
cd web-ui
docker-compose down
docker-compose up -d --build
```

### Option 3: Disable Optimizations (Keep Running)
```bash
docker-compose stop backend
docker-compose run -d --name hunyuan-api \
  -e ENABLE_CACHE=false \
  -e ENABLE_ADAPTIVE_STEPS=false \
  backend
```

---

## Troubleshooting

### Redis Won't Start
```bash
# Check Redis logs
docker-compose logs redis

# Verify port 6379 is free
netstat -tuln | grep 6379

# Restart Redis specifically
docker-compose restart redis
```

### Backend Can't Connect to Redis
```bash
# Check network
docker network inspect web-ui_hunyuan-net

# Verify Redis is reachable from backend
docker exec hunyuan-api ping redis -c 3

# Check environment variables
docker exec hunyuan-api env | grep REDIS
```

### Frontend Not Showing New Features
```bash
# Clear browser cache (Ctrl+Shift+R)
# Or rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Missing Python Dependencies
```bash
# Check if redis package is installed
docker exec hunyuan-api pip list | grep redis

# If missing, rebuild
docker-compose build --no-cache backend
docker-compose up -d backend
```

---

## Performance Expectations

### Before Optimizations
- Simple prompt: 30 steps, ~7 min, $0.27
- Complex prompt: 40 steps, ~9 min, $0.36
- Cache hit rate: 0%

### After Optimizations (Phase 1)
- Simple prompt: 18 steps, ~4 min, $0.16 (40% faster, 41% cheaper)
- Complex prompt: 40 steps, ~9 min, $0.36 (same quality for complex)
- Cached prompt: Same steps, ~15% faster (embedding reuse)
- Average speedup: 20-25%
- Cache hit rate after 10 videos: ~30-50%

---

## Next Steps (Phase 2)

After Phase 1 is stable, we can implement:

1. **Batch Processing**: Process 4 videos simultaneously
2. **Frame Interpolation**: Generate fewer frames, interpolate more
3. **Multi-GPU Support**: Load balance across multiple droplets
4. **Model Distillation**: Create smaller specialized models

Estimated additional speedup: 2-3x

---

## Success Metrics

✅ Redis cache operational (PONG response)
✅ Backend shows "Redis cache connected"
✅ Frontend displays quality tier selector
✅ Stats bar shows "Cache Hit Rate" and "Avg Steps"
✅ Simple prompts use <25 steps
✅ Complex prompts use >30 steps
✅ Repeated prompts show cache hit badge
✅ No errors in logs
✅ Video generation still works correctly

---

## Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify all services running: `docker-compose ps`
3. Test Redis: `docker exec hunyuan-cache redis-cli ping`
4. Restart: `docker-compose restart`
5. Rollback if needed (see Rollback Plan above)

**Current Status**: Ready to deploy! 🚀
