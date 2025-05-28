#!/bin/bash

# AI Code Reviewer - Service Startup Script
# Khởi chạy toàn bộ services sử dụng Docker Compose

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AI Code Reviewer - Starting All Services${NC}"
echo "=============================================="

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if docker-compose is available
check_docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        print_error "Docker Compose is not available. Please install docker-compose or use Docker with compose plugin."
        exit 1
    fi
    print_success "Docker Compose found: $COMPOSE_CMD"
}

# Function to create environment file if not exists
create_env_file() {
    if [[ ! -f .env ]]; then
        print_warning ".env file not found. Creating default environment file..."
        cat > .env << 'EOF'
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=aicode
POSTGRES_PASSWORD=aicode123
POSTGRES_DB=aicode_reviewer

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=10080

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Frontend Configuration
VITE_API_URL=http://localhost:8000

# LLM Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
EOF
        print_success "Created default .env file"
    else
        print_success ".env file already exists"
    fi
}

# Function to create required directories
create_directories() {
    print_status "Creating required directories..."
    
    # Neo4j directories
    mkdir -p neo4j/data neo4j/logs neo4j/import neo4j/plugins
    
    # Backend logs
    mkdir -p logs
    
    print_success "Directories created"
}

# Function to pull latest images
pull_images() {
    print_status "Pulling latest Docker images..."
    $COMPOSE_CMD pull
    print_success "Images updated"
}

# Function to build custom images
build_images() {
    print_status "Building custom Docker images..."
    $COMPOSE_CMD build --no-cache
    print_success "Images built"
}

# Function to start services
start_services() {
    print_status "Starting services with Docker Compose..."
    
    # Start services in detached mode
    $COMPOSE_CMD up -d
    
    print_success "Services started"
}

# Function to wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    local max_attempts=60
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        local healthy_services=0
        local total_services=5  # neo4j, postgres, redis, backend, frontend
        
        # Check Neo4j
        if docker exec aicode-reviewer-neo4j cypher-shell "RETURN 1" >/dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check PostgreSQL
        if docker exec aicode-reviewer-postgres pg_isready -U aicode >/dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check Redis
        if docker exec aicode-reviewer-redis redis-cli ping >/dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check Backend
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check Frontend
        if curl -f http://localhost:5173 >/dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        if [[ $healthy_services -eq $total_services ]]; then
            print_success "All services are healthy and ready!"
            break
        fi
        
        echo -n "."
        sleep 5
        ((attempt++))
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        print_warning "Some services may not be fully ready yet. Check service logs for details."
    fi
}

# Function to show service status
show_status() {
    echo ""
    print_status "Service Status:"
    $COMPOSE_CMD ps
    
    echo ""
    print_status "Service URLs:"
    echo "🌐 Frontend:     http://localhost:5173"
    echo "🔧 Backend API:  http://localhost:8000"
    echo "📊 Neo4j:       http://localhost:7474"
    echo "🗄️  PostgreSQL:  localhost:5432"
    echo "🔄 Redis:       localhost:6379"
}

# Function to show logs
show_logs() {
    if [[ "$1" == "--logs" ]] || [[ "$1" == "-l" ]]; then
        echo ""
        print_status "Following service logs (Ctrl+C to stop)..."
        $COMPOSE_CMD logs -f
    fi
}

# Main execution
main() {
    local follow_logs=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --logs|-l)
                follow_logs=true
                shift
                ;;
            --build|-b)
                BUILD_IMAGES=true
                shift
                ;;
            --pull|-p)
                PULL_IMAGES=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --logs, -l     Follow service logs after startup"
                echo "  --build, -b    Force rebuild of Docker images"
                echo "  --pull, -p     Pull latest base images before starting"
                echo "  --help, -h     Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Execution steps
    check_docker
    check_docker_compose
    create_env_file
    create_directories
    
    if [[ "$PULL_IMAGES" == "true" ]]; then
        pull_images
    fi
    
    if [[ "$BUILD_IMAGES" == "true" ]]; then
        build_images
    fi
    
    start_services
    wait_for_services
    show_status
    
    echo ""
    print_success "🎉 All services are running!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Initialize database: ./scripts/init-database.sh"
    echo "  2. Access frontend: http://localhost:5173"
    echo "  3. Access API docs: http://localhost:8000/docs"
    echo "  4. View logs: $COMPOSE_CMD logs -f"
    echo "  5. Stop services: $COMPOSE_CMD down"
    
    if [[ "$follow_logs" == "true" ]]; then
        show_logs
    fi
}

# Handle script termination
cleanup() {
    echo ""
    print_status "Script interrupted. Services are still running."
    echo "To stop services, run: $COMPOSE_CMD down"
    exit 130
}

trap cleanup SIGINT SIGTERM

# Run main function
main "$@" 