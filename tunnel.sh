#!/bin/bash
# SSH Port Forwarding to Access HunyuanVideo Web UI
# Run this on your local machine

echo "🚀 Starting SSH tunnel to HunyuanVideo Studio..."
echo ""
echo "Once connected, access the web UI at:"
echo "  Web UI:  http://localhost:3000"
echo "  API:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the tunnel"
echo ""

ssh -L 3000:localhost:3000 -L 8000:localhost:8000 -N root@143.198.39.124
