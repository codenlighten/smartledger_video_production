# HunyuanVideo Web UI

Modern, responsive web interface for HunyuanVideo generation with real-time updates.

## Features

- 🎨 **Modern UI/UX** - Clean, dark-themed interface built with React and Tailwind CSS
- ⚡ **Real-time Updates** - WebSocket-based live progress tracking
- 📊 **Statistics Dashboard** - Track generations, GPU time, and costs
- 🎬 **Video Gallery** - Browse, filter, and manage generated videos
- 🎛️ **Advanced Controls** - Full parameter customization (resolution, steps, CFG, seed)
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🔄 **Queue Management** - Handle multiple generation jobs

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│   React     │────▶│   FastAPI   │────▶│  HunyuanVideo    │
│   Frontend  │◀────│   Backend   │◀────│  Docker Container│
│  (Port 3000)│ WS  │  (Port 8000)│     │                  │
└─────────────┘     └─────────────┘     └──────────────────┘
```

### Tech Stack

**Frontend:**
- React 18 with Vite
- Tailwind CSS for styling
- Lucide React for icons
- Axios for HTTP requests
- Native WebSocket API

**Backend:**
- FastAPI for REST API
- WebSockets for real-time updates
- Async/await for concurrent operations
- Docker SDK for container management

## Quick Start

### Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm install
npm run dev
```

Access at: http://localhost:3000

### Production (Docker)

```bash
docker-compose up -d
```

Access at: http://YOUR_SERVER_IP:3000

## API Endpoints

### REST API

- `POST /api/generate` - Start video generation
- `GET /api/jobs` - List all jobs
- `GET /api/jobs/{job_id}` - Get job status
- `DELETE /api/jobs/{job_id}` - Delete job
- `GET /api/video/{job_id}` - Download video
- `GET /api/thumbnail/{job_id}` - Get thumbnail
- `GET /api/stats` - Get statistics
- `GET /api/health` - Health check

### WebSocket

- `WS /ws` - Real-time job updates

## Configuration

### Environment Variables

```bash
# Backend
RESULTS_DIR=/opt/hunyuan-video/results

# Frontend
VITE_API_URL=http://localhost:8000
```

### Video Generation Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `video_size` | 720 | 540, 720 | Resolution |
| `video_length` | 129 | 1-129 | Number of frames |
| `infer_steps` | 50 | 30-100 | Quality (higher = better) |
| `cfg_scale` | 6.0 | 1.0-20.0 | Guidance strength |
| `seed` | Random | Any int | Reproducibility |
| `flow_reverse` | true | bool | Flow reversal |

## Deployment to DigitalOcean

1. **Upload to server:**
```bash
cd /home/greg/dev/hunyuan-video
scp -r web-ui root@143.198.39.124:/root/
```

2. **Build and start:**
```bash
ssh root@143.198.39.124
cd /root/web-ui
docker-compose up -d --build
```

3. **Access:**
- Frontend: http://143.198.39.124:3000
- API: http://143.198.39.124:8000
- API Docs: http://143.198.39.124:8000/docs

## Features Showcase

### Generation Form
- Text prompt with examples
- Resolution selector (540p/720p)
- Frame count (1-129)
- Quality steps (30-100)
- Advanced settings (seed, CFG scale, flow reversal)
- Real-time cost estimation

### Video Gallery
- Filterable by status (all, completed, processing, queued, failed)
- Video thumbnails
- Progress bars for active generations
- Download and delete actions
- Error messages for failed jobs

### Statistics Dashboard
- Total videos generated
- Active jobs count
- Average generation time
- Total GPU time and cost

### Real-time Updates
- WebSocket connection for live progress
- Automatic reconnection
- Progress percentage display
- Status badge updates

## Cost Tracking

The UI automatically calculates:
- Per-video cost: **$0.29** (based on H100 $3.39/hr, ~5min generation)
- Total GPU time used
- Estimated monthly costs at scale

## Performance

- Backend handles concurrent generations via async
- Frontend uses React hooks for efficient re-renders
- WebSocket reduces polling overhead
- Nginx caching for static assets
- Gzip compression enabled

## Security Considerations

For production:
1. Add authentication (JWT tokens)
2. Rate limiting on API endpoints
3. HTTPS with Let's Encrypt
4. CORS configuration
5. Input validation and sanitization

## Monitoring

Health check endpoint provides:
- API status
- HunyuanVideo container status
- Active job count
- Total generations

## Troubleshooting

**WebSocket not connecting:**
```bash
# Check backend logs
docker logs hunyuan-api

# Check WebSocket URL in browser console
```

**Videos not appearing:**
```bash
# Check results directory permissions
ls -la /opt/hunyuan-video/results/

# Check Docker volume mounts
docker inspect hunyuan-api | grep Mounts
```

**Frontend not building:**
```bash
cd frontend
rm -rf node_modules dist
npm install
npm run build
```

## Future Enhancements

- [ ] User authentication
- [ ] Video editing (trim, crop)
- [ ] Batch generation
- [ ] Style presets
- [ ] Video2Video mode
- [ ] Cost analytics dashboard
- [ ] Export to cloud storage
- [ ] API rate limiting
- [ ] Webhook notifications
- [ ] Multi-user support

## License

Built for HunyuanVideo by Tencent. Web UI is MIT licensed.
