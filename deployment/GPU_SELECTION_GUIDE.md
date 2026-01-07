# GPU Selection Guide for HunyuanVideo

## Quick Reference

| GPU | VRAM | Cost/hr | Status | Best For |
|-----|------|---------|--------|----------|
| **H200** | **141GB** | **$3.44** | ✅ **RECOMMENDED** | Development, testing, production |
| H100 | 80GB | $3.39 | ✅ Works | Budget-conscious deployments |
| H200 x8 | 1.1TB | $27.52 | ✅ Excellent | High-throughput production |
| H100 x8 | 640GB | $23.92 | ✅ Good | Multi-GPU parallel inference |
| L40S | 48GB | $1.57 | ⚠️ **NOT RECOMMENDED** | Below minimum requirements |
| RTX 6000 ADA | 48GB | $1.57 | ⚠️ **NOT RECOMMENDED** | Below minimum requirements |
| RTX 4000 ADA | 20GB | $0.76 | ❌ **UNUSABLE** | Way too small |

## Detailed Analysis

### ⭐ H200 (Single GPU) - RECOMMENDED

**Specs:**
- 141GB VRAM
- 24 vCPU
- 240 GB RAM
- $3.44/hour

**Why it's the best choice:**
- **76% more VRAM** than H100 for only **$0.05/hr more**
- Plenty of headroom for 720p generation
- Can experiment with higher resolutions (potentially 1080p)
- Support longer videos (200+ frames)
- Room for multiple concurrent requests
- Future-proof for model updates

**Cost analysis:**
- Monthly (24/7): $2,511
- vs H100 monthly: $2,475 (only $36 difference!)
- **Best value per dollar of VRAM**

**Use cases:**
- Development and testing
- Production single-instance deployment
- Custom fine-tuning experiments
- Research and exploration

---

### H100 (Single GPU) - Budget Option

**Specs:**
- 80GB VRAM
- 20 vCPU
- 240 GB RAM
- $3.39/hour

**Pros:**
- Meets minimum requirements for 720p
- Slightly cheaper than H200 ($0.05/hr less)
- Proven configuration

**Cons:**
- Tight on memory (60GB required)
- Requires CPU offload
- No room for experimentation
- Cannot increase resolution or length
- Limited to standard configurations

**When to choose:**
- You're on a strict budget
- Only need standard 720p × 129 frames
- Not planning to modify or experiment

**Cost:**
- Monthly: $2,475

---

### H200 x8 / H100 x8 - Production Scale

**H200 x8 Specs:**
- 1.1TB total VRAM
- 192 vCPU
- 1920 GB RAM
- $27.52/hour ($3.44 per GPU)

**H100 x8 Specs:**
- 640GB total VRAM
- 160 vCPU
- 1920 GB RAM
- $23.92/hour ($2.99 per GPU)

**Benefits:**
- **5-8x faster inference** with xDiT parallel execution
- Handle multiple users simultaneously
- Process 80-96+ videos per hour
- Suitable for high-traffic SaaS platforms
- Load balancing across GPUs

**Cost analysis:**
- H200 x8 monthly: $20,090
- H100 x8 monthly: $17,461
- Effective cost per video: $0.29-0.34

**When to choose:**
- Production SaaS with high demand
- Need to serve multiple concurrent users
- Want fastest possible generation times
- Have consistent high volume (100+ videos/day)

---

### ⚠️ L40S / RTX 6000 ADA - NOT RECOMMENDED

**Specs:**
- 48GB VRAM
- 8 vCPU
- 64 GB RAM
- $1.57/hour

**Why it won't work:**

HunyuanVideo requires:
- **720p:** 60GB VRAM minimum
- **540p:** 45GB VRAM minimum

L40S provides: **48GB VRAM**

**The problem:**
- Only 3GB headroom at 540p (minimum resolution)
- Will likely cause OOM (Out of Memory) errors
- Even with FP8 quantization (~10GB savings), still too tight
- No room for CUDA runtime, buffers, overhead

**Could it work?**

Theoretically with extreme optimization:
```bash
python3 sample_video.py \
    --dit-weight /path/to/model_fp8.pt \
    --video-size 544 960 \
    --video-length 65 \     # Half frames (2.5s videos)
    --infer-steps 30 \      # Fewer steps
    --use-fp8 \
    --use-cpu-offload \
    --save-path ./results
```

**Expected outcome:** Still likely to fail or produce poor quality

**Verdict:** Not worth the trouble. Spend the extra $1.87/hr for H100.

---

### ❌ RTX 4000 ADA - UNUSABLE

**Specs:**
- 20GB VRAM
- $0.76/hour

**Status:** Impossible. You need 60GB minimum. This has 20GB.

---

## Memory Requirements by Resolution

| Resolution | Frames | VRAM Required | H200 | H100 | L40S |
|------------|--------|---------------|------|------|------|
| 544×960 (540p) | 129 | 45GB | ✅ | ✅ | ⚠️ |
| 720×1280 (720p) | 129 | 60GB | ✅ | ✅ | ❌ |
| 1080×1920 (1080p)* | 129 | ~80-90GB | ✅ | ⚠️ | ❌ |
| 720×1280 (720p) | 200* | ~75-85GB | ✅ | ⚠️ | ❌ |

*Experimental - not officially supported

---

## Cost Optimization Strategies

### Strategy 1: On-Demand Usage
- Start droplet only when needed
- Generate videos in batches
- Destroy when done
- **Best for:** < 20 videos/day

### Strategy 2: Reserved Hours
- Keep H200 running during business hours (8hrs/day)
- Cost: $3.44 × 8 × 30 = $826/month
- Generate ~96 videos/day
- **Best for:** Regular but not 24/7 usage

### Strategy 3: 24/7 Always-On
- Keep H200 running continuously
- Cost: $2,511/month
- Unlimited capacity (~8,760 videos/month)
- **Best for:** Production SaaS platforms

### Strategy 4: Hybrid Multi-GPU
- Use H200 x1 for development
- Scale to H200 x8 for peak hours via API
- Destroy extra GPUs when traffic drops
- **Best for:** Variable workload patterns

---

## Decision Tree

```
Start Here
│
├─ Need < 10 videos/day?
│  └─ Use Veo 3.1 API (pay-per-use)
│
├─ Need 10-50 videos/day?
│  └─ H200 single GPU (on-demand)
│
├─ Need 50-500 videos/day?
│  └─ H200 single GPU (24/7)
│
├─ Need 500+ videos/day?
│  └─ H200 x8 (parallel inference)
│
└─ Maximum performance needed?
   └─ H200 x8 (24/7)
```

---

## Recommendations Summary

### For Most Users: **H200 (Single GPU)**
- Best value: $0.05/hr more than H100
- 76% more VRAM
- Room to grow and experiment
- Cost: $3.44/hr

### For High Volume: **H200 x8**
- 5-8x faster generation
- Handle multiple concurrent users
- Cost: $27.52/hr

### Avoid: **L40S, RTX 6000 ADA, RTX 4000 ADA**
- Below minimum requirements
- Will cause OOM errors
- Not worth the savings

---

## Testing Before Committing

Before running 24/7:

1. **Create H200 droplet** using deployment scripts
2. **Download models** (~30GB, one-time)
3. **Generate test videos** at your target resolution
4. **Monitor VRAM usage** with `nvidia-smi`
5. **Calculate your throughput** (videos/hour)
6. **Estimate costs** based on your volume

**One hour test:** $3.44 to validate entire setup
