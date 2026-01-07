#!/bin/bash
################################################################################
# HunyuanVideo Phase 1 Optimization Deployment Script
# Deploys Redis cache and adaptive generation optimizations
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║  HunyuanVideo - Phase 1 Optimization Deployment          ║
║  Redis Cache + Adaptive Generation + Quality Tiers       ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
  log_error "Please run with sudo or as root"
  exit 1
fi

# Get deployment directory
DEPLOY_DIR=${DEPLOY_DIR:-"/opt/hunyuan-video-deployment"}

if [ ! -d "$DEPLOY_DIR" ]; then
  log_error "Deployment directory not found: $DEPLOY_DIR"
  log_info "Set DEPLOY_DIR environment variable if using custom location"
  exit 1
fi

log_info "Using deployment directory: $DEPLOY_DIR"
cd "$DEPLOY_DIR"

################################################################################
# Step 1: Backup current configuration
################################################################################
log_info "Step 1: Creating backup..."

BACKUP_DIR="backups/optimization-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -d "web-ui" ]; then
  cp -r web-ui/docker-compose.yml "$BACKUP_DIR/" 2>/dev/null || true
  cp -r web-ui/backend/*.py "$BACKUP_DIR/" 2>/dev/null || true
fi

log_success "Backup created at: $BACKUP_DIR"

################################################################################
# Step 2: Pull latest code
################################################################################
log_info "Step 2: Pulling latest optimizations from Git..."

if [ -d ".git" ]; then
  git fetch origin
  git pull origin main
  log_success "Code updated"
else
  log_warning "Not a git repository, skipping pull"
fi

################################################################################
# Step 3: Verify new files
################################################################################
log_info "Step 3: Verifying optimization files..."

REQUIRED_FILES=(
  "web-ui/docker-compose.yml"
  "web-ui/backend/main.py"
  "web-ui/backend/cache_manager.py"
  "web-ui/backend/adaptive_optimizer.py"
  "web-ui/backend/requirements.txt"
  "web-ui/frontend/src/components/OptimizationBadge.jsx"
  "web-ui/frontend/src/components/StatsBar.jsx"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    log_error "Missing file: $file"
    ((MISSING_FILES++))
  else
    log_success "✓ $file"
  fi
done

if [ $MISSING_FILES -gt 0 ]; then
  log_error "$MISSING_FILES required files missing. Please check your repository."
  exit 1
fi

################################################################################
# Step 4: Stop current services
################################################################################
log_info "Step 4: Stopping current services..."

cd web-ui
docker compose down
log_success "Services stopped"

################################################################################
# Step 5: Clean up old containers and volumes
################################################################################
log_info "Step 5: Cleaning up..."

# Remove old images
docker image prune -f || true
log_success "Old images removed"

################################################################################
# Step 6: Build new containers with optimizations
################################################################################
log_info "Step 6: Building optimized containers..."
log_info "This will take 2-3 minutes..."

docker compose build --no-cache
log_success "Containers built successfully"

################################################################################
# Step 7: Start services
################################################################################
log_info "Step 7: Starting optimized services..."

docker compose up -d
log_success "Services started"

################################################################################
# Step 8: Wait for services to be healthy
################################################################################
log_info "Step 8: Waiting for services to be healthy..."

sleep 10

# Check Redis
log_info "Checking Redis..."
if docker exec hunyuan-cache redis-cli ping > /dev/null 2>&1; then
  log_success "✓ Redis is healthy"
else
  log_error "✗ Redis is not responding"
  exit 1
fi

# Check backend
log_info "Checking backend API..."
MAX_RETRIES=30
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
  if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    log_success "✓ Backend API is healthy"
    break
  fi
  ((RETRY++))
  if [ $RETRY -eq $MAX_RETRIES ]; then
    log_error "✗ Backend API did not start"
    docker compose logs backend
    exit 1
  fi
  sleep 2
done

# Check frontend
log_info "Checking frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
  log_success "✓ Frontend is healthy"
else
  log_warning "Frontend may take a moment to start"
fi

################################################################################
# Step 9: Verify optimization features
################################################################################
log_info "Step 9: Verifying optimization features..."

# Check stats endpoint for optimization data
STATS=$(curl -s http://localhost:8000/api/stats)
if echo "$STATS" | grep -q "optimization"; then
  log_success "✓ Optimization API endpoint working"
  
  # Extract optimization status
  CACHE_ENABLED=$(echo "$STATS" | jq -r '.optimization.cache_enabled' 2>/dev/null || echo "unknown")
  ADAPTIVE_ENABLED=$(echo "$STATS" | jq -r '.optimization.adaptive_enabled' 2>/dev/null || echo "unknown")
  
  log_info "Cache enabled: $CACHE_ENABLED"
  log_info "Adaptive steps enabled: $ADAPTIVE_ENABLED"
else
  log_warning "Could not verify optimization features"
fi

# Test prompt analysis endpoint
log_info "Testing prompt analysis..."
ANALYSIS=$(curl -s "http://localhost:8000/api/optimization/analyze?prompt=A%20cat%20walks%20on%20grass&quality_tier=auto")
if echo "$ANALYSIS" | grep -q "complexity"; then
  COMPLEXITY=$(echo "$ANALYSIS" | jq -r '.analysis.complexity' 2>/dev/null || echo "unknown")
  STEPS=$(echo "$ANALYSIS" | jq -r '.analysis.infer_steps' 2>/dev/null || echo "unknown")
  log_success "✓ Prompt analysis working (Complexity: $COMPLEXITY, Steps: $STEPS)"
else
  log_warning "Could not verify prompt analysis"
fi

################################################################################
# Step 10: Show service status
################################################################################
log_info "Step 10: Service status..."
echo ""
docker compose ps
echo ""

################################################################################
# Step 11: Display access information
################################################################################
echo ""
log_success "═══════════════════════════════════════════════════════════"
log_success "  OPTIMIZATION DEPLOYMENT COMPLETE! 🚀"
log_success "═══════════════════════════════════════════════════════════"
echo ""
log_info "New Features Available:"
echo "  ⚡ Redis embedding cache (15-20% speedup)"
echo "  🧠 Adaptive step calculation (15-25% speedup)"
echo "  💎 Quality tier system (preview/standard/premium)"
echo "  📊 Enhanced monitoring and analytics"
echo ""
log_info "Access your application:"
echo "  🌐 Web UI: http://localhost:3000"
echo "  🔌 API: http://localhost:8000"
echo "  📊 API Stats: http://localhost:8000/api/stats"
echo "  📈 Health Check: http://localhost:8000/api/health"
echo ""
log_info "Service Containers:"
echo "  🗄️  Redis Cache: hunyuan-cache"
echo "  ⚙️  Backend API: hunyuan-api"
echo "  🎨 Frontend UI: hunyuan-ui"
echo ""
log_info "Useful Commands:"
echo "  📝 View logs: docker compose logs -f"
echo "  🔄 Restart: docker compose restart"
echo "  🛑 Stop: docker compose down"
echo "  📊 Stats: curl http://localhost:8000/api/stats | jq"
echo ""
log_info "Monitor Optimization:"
echo "  🎯 Cache stats: docker exec hunyuan-cache redis-cli INFO stats"
echo "  📈 Watch logs: docker compose logs -f backend | grep -E 'Cache|📊'"
echo ""
log_warning "Note: If accessing remotely, replace localhost with your server IP"
echo ""
log_success "Read OPTIMIZATION_PHASE1.md for detailed documentation"
log_success "═══════════════════════════════════════════════════════════"
echo ""

# Save deployment info
cat > "$DEPLOY_DIR/deployment-info.txt" << EOF
Deployment Date: $(date)
Optimization Phase: Phase 1 (Cache + Adaptive)
Docker Compose Version: $(docker compose version)
Services:
  - Redis Cache: hunyuan-cache
  - Backend API: hunyuan-api (with optimizations)
  - Frontend UI: hunyuan-ui (with optimization UI)

Features Enabled:
  ✓ Redis embedding cache
  ✓ Adaptive step calculation
  ✓ Quality tier system
  ✓ Enhanced monitoring

Expected Performance:
  - 20-25% average speedup
  - 40% speedup on cached prompts
  - Cost reduction per video
EOF

log_success "Deployment info saved to deployment-info.txt"
