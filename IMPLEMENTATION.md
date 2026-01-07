# HunyuanVideo Web UI - Production Deployment

A complete, production-ready implementation of Tencent's HunyuanVideo text-to-video model with a modern web interface, GPU support, and real-time generation tracking.

## 🎬 Features

- **Text-to-Video Generation**: Generate videos from text prompts using HunyuanVideo's 13B transformer
- **Multiple Resolutions**: 540p (544×960 portrait) and 720p (720×1280 landscape)
- **Real-time Progress Tracking**: WebSocket-based live updates during generation
- **Video Playback**: Inline HTML5 video player with native controls
- **Modern Dark UI**: React 18 + Tailwind CSS with responsive design
- **GPU Acceleration**: NVIDIA CUDA support with CPU offloading fallback
- **Horizontal Scaling**: Stateless backend design for multi-instance deployment
- **Production Ready**: HTTPS/SSL, reverse proxy, error handling, memory management

## 📊 Performance

- **Generation Speed**: ~7-8 minutes per 540p video (30 inference steps)
- **Memory Efficiency**: Properly freed GPU memory after each generation (no leaks)
- **Throughput**: Sequential generations with full GPU cleanup
- **Video Quality**: 129 frames (~5 seconds) at 25fps with high quality

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI (Python 3.11)
- **Orchestration**: Docker container execution
- **Job Management**: In-memory queue with WebSocket broadcast
- **API**: RESTful endpoints + WebSocket for real-time updates

### Frontend Stack
- **Framework**: React 18 + Vite
- **UI Library**: Tailwind CSS
- **Icons**: Lucide React
- **State Management**: React Hooks
- **Real-time**: WebSocket consumer for live status

### Infrastructure
- **Container Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx with HTTPS/SSL
- **Model Hosting**: HuggingFace Hub (auto-downloaded)
- **GPU Support**: NVIDIA CUDA 12.9 with 80GB HBM3

## 📦 Deployment

### Prerequisites
- Docker & Docker Compose
- NVIDIA GPU (tested on H100 80GB HBM3)
- 80GB+ storage for model weights
- Python 3.11+ (for local development)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/codenlighten/smartledger_video_production.git
cd smartledger_video_production

# 2. Configure environment
cp web-ui/.env.example web-ui/.env
# Edit .env with your settings

# 3. Start deployment
cd web-ui
docker-compose up -d

# 4. Access web UI
# Local: http://localhost:3000
# Remote: https://your-domain.com (configure DNS + SSL first)
```

### DigitalOcean Deployment (Tested)

**Hardware**: H100 GPU Droplet ($3.39/hour)
- 8 CPU cores
- 80GB NVIDIA H100 HBM3 GPU
- 256GB RAM
- 1TB SSD storage

**Steps**:
1. Create droplet with Ubuntu 22.04
2. Install Docker & Docker Compose
3. Clone this repository
4. Configure DNS for domain
5. Generate Let's Encrypt SSL certificate
6. Run docker-compose up -d

## 🎯 API Endpoints

### Video Generation
```bash
POST /api/generate
{
  "prompt": "A cat walking in snow",
  "video_size": 540,           # 540 or 720
  "video_length": 129,          # 1-129 frames
  "infer_steps": 30,            # 20-100 steps
  "seed": 12345,                # Optional random seed
  "cfg_scale": 6.0,             # Classifier-free guidance scale
  "flow_reverse": true          # Enable flow reversal
}
```

### Job Management
```bash
GET /api/jobs                   # List all jobs
GET /api/jobs/{job_id}          # Get specific job status
DELETE /api/jobs/{job_id}       # Delete job and results
GET /api/video/{job_id}         # Download generated video
GET /api/thumbnail/{job_id}     # Get video thumbnail
GET /api/stats                  # Get generation statistics
GET /api/health                 # Health check
```

### WebSocket
```
WS /ws
Receives: {"type": "status_update", "job": {...}}
```

## 📁 Project Structure

```
web-ui/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend container
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app component
│   │   ├── main.jsx         # React entry point
│   │   ├── index.css        # Global styles
│   │   ├── components/
│   │   │   ├── VideoCard.jsx        # Video display component
│   │   │   ├── GenerationForm.jsx   # Input form
│   │   │   └── StatsBar.jsx         # Statistics
│   │   ├── hooks/
│   │   │   └── useApi.js    # API communication
│   │   └── ...
│   ├── package.json         # Dependencies
│   ├── Dockerfile           # Frontend container
│   ├── nginx.conf           # Nginx configuration
│   └── tailwind.config.js   # Tailwind setup
└── docker-compose.yml       # Service orchestration
```

## 🔧 Configuration

### Environment Variables

```env
# Backend
PYTHON_ENV=production
LOG_LEVEL=info

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Nginx
SSL_CERTIFICATE=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_PRIVATE_KEY=/etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### Model Configuration

Models are automatically downloaded from HuggingFace Hub:
- **Text Encoder**: `xtuner/llava-llama-3-8b-v1_1-transformers` (15GB)
- **Text Encoder 2**: OpenAI CLIP ViT-Large (6.4GB)
- **Main Model**: `Tencent-Hunyuan/hunyuan-video-t2v-720p` (38GB)

## 🚀 Performance Tuning

### Memory Optimization
```python
# Enable CPU offloading for dtype conversion
--use-cpu-offload

# Enable flow reversal for better quality
--flow-reverse

# Reduce steps for faster generation
--infer-steps 20  # Fast (3-4 min) vs 50 (8+ min)
```

### GPU Management
- Automatic cleanup after each generation
- CPU offload fallback for memory constraints
- Proper dtype handling for mixed precision

## 📊 Monitoring

### Health Checks
```bash
curl http://localhost:8000/api/health
```

### Statistics
```bash
curl http://localhost:8000/api/stats
# Returns:
# {
#   "total_generations": 5,
#   "completed": 4,
#   "failed": 0,
#   "in_progress": 1,
#   "queued": 0,
#   "avg_duration": 425.5,
#   "total_duration": 1702.0
# }
```

### Logs
```bash
# Backend
docker logs hunyuan-api -f

# Frontend
docker logs hunyuan-ui -f

# GPU Container
docker logs hunyuan-video -f
```

## 🐛 Troubleshooting

### Page Shows Blank Screen
- Check browser console for JavaScript errors
- Verify frontend container is running: `docker ps`
- Check frontend logs: `docker logs hunyuan-ui`
- Clear browser cache and reload

### Video Generation Fails (CUDA OOM)
- Reduce inference steps: `infer_steps: 20`
- Ensure no other CUDA processes running: `nvidia-smi`
- Check GPU memory: `docker exec hunyuan-video nvidia-smi`

### Videos Not Playing
- Verify backend is running: `docker logs hunyuan-api`
- Check video file exists: `docker exec hunyuan-video ls /workspace/repo/results/`
- Verify browser supports MP4/H.264

### WebSocket Connection Issues
- Check Nginx reverse proxy configuration
- Verify WebSocket upgrade headers in Nginx
- Check CORS settings in FastAPI

## 📝 API Response Examples

### Successful Generation
```json
{
  "job_id": "06831899-2fb4-44c6-ad35-4242aaac044f",
  "status": "completed",
  "prompt": "A golden sunset over mountains",
  "progress": 100,
  "created_at": "2026-01-07T22:38:00.000000",
  "completed_at": "2026-01-07T22:44:51.095036",
  "video_path": "/opt/hunyuan-video/results/06831899-2fb4-44c6-ad35-4242aaac044f/video.mp4",
  "thumbnail_path": "/opt/hunyuan-video/results/06831899-2fb4-44c6-ad35-4242aaac044f/thumbnail.jpg",
  "duration": 391.095036,
  "error": null
}
```

### Generation In Progress
```json
{
  "job_id": "12345678-abcd-efgh-ijkl-mnopqrstuvwx",
  "status": "processing",
  "progress": 45,
  "prompt": "A cat walking in snow",
  "created_at": "2026-01-07T22:50:00.000000",
  ...
}
```

## 🔐 Security Considerations

- **API Key**: Add authentication layer for production
- **Rate Limiting**: Implement per-user rate limits
- **Input Validation**: All prompts validated server-side
- **HTTPS/SSL**: Required for production deployment
- **CORS**: Configured to allow trusted origins only

## 📈 Scaling Strategies

### Horizontal Scaling
1. **Stateless Backend**: Job state stored externally (Redis/DB)
2. **Load Balancer**: Nginx upstream configuration
3. **Multiple GPUs**: Queue distribution across GPUs

### Vertical Scaling
1. **Batch Processing**: Multiple sequential generations
2. **Step Reduction**: Lower inference steps for faster throughput
3. **Resolution Optimization**: Use 540p for higher throughput

## 📄 License

Based on Tencent's HunyuanVideo under CC BY-NC 4.0

## 🙏 Credits

- **HunyuanVideo**: Tencent Research
- **Text Encoders**: XTuner (LLaVA), OpenAI (CLIP)
- **Infrastructure**: DigitalOcean GPU Droplet

## 📞 Support

For issues or questions:
1. Check logs: `docker logs [service-name]`
2. Review troubleshooting section above
3. Check GitHub issues
4. Open a new issue with detailed error messages

---

**Status**: ✅ Production Ready  
**Last Updated**: January 7, 2026  
**Tested On**: DigitalOcean H100 GPU Droplet with Ubuntu 22.04
