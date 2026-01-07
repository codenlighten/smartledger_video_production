#!/bin/bash
# Health check: verifies Gradio server is responding and GPU is accessible
set -e

SERVER_URL="http://127.0.0.1:7860"
LOG_FILE="/opt/hunyuan-video/logs/healthcheck.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Running health check..."

# Check Gradio HTTP endpoint
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVER_URL")
if [ "$STATUS_CODE" != "200" ] && [ "$STATUS_CODE" != "302" ]; then
    log "ERROR: Gradio not responding (HTTP $STATUS_CODE)"
    exit 1
fi

# Check GPU availability
if ! nvidia-smi > /dev/null 2>&1; then
    log "ERROR: GPU not accessible"
    exit 1
fi

gpu_util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -n1)
log "GPU utilization: ${gpu_util}%"

log "Health check passed"
