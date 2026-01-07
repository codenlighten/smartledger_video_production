#!/bin/bash
# Basic monitoring: logs GPU + process info periodically

INTERVAL=${1:-30}
LOG_FILE="/opt/hunyuan-video/logs/monitor.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting monitor with interval ${INTERVAL}s"

while true; do
    log "--- GPU ---"
    nvidia-smi | tee -a "$LOG_FILE"
    log "--- TOP (python) ---"
    ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n 15 | grep python | tee -a "$LOG_FILE" || true
    sleep "$INTERVAL"
done
