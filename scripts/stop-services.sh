#!/bin/bash

# AI Code Reviewer - Service Stop Script
# Dừng toàn bộ services và cleanup

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}🛑 AI Code Reviewer - Stopping All Services${NC}"
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

# Function to stop services
stop_services() {
    print_status "Stopping Docker Compose services..."
    
    if $COMPOSE_CMD ps --quiet | head -1 >/dev/null 2>&1; then
        $COMPOSE_CMD down
        print_success "Services stopped"
    else
        print_warning "No running services found"
    fi
}

# Function to remove volumes
remove_volumes() {
    if [[ "$1" == "--volumes" ]] || [[ "$1" == "-v" ]]; then
        print_warning "This will remove all data volumes. Are you sure? (y/N)"
        read -r confirmation
        
        if [[ "$confirmation" =~ ^[Yy]$ ]]; then
            print_status "Removing Docker volumes..."
            $COMPOSE_CMD down -v
            print_success "Volumes removed"
        else
            print_status "Volume removal cancelled"
        fi
    fi
}

# Function to remove images
remove_images() {
    if [[ "$1" == "--images" ]] || [[ "$1" == "-i" ]]; then
        print_status "Removing Docker images..."
        
        # Remove custom images
        docker rmi aicode-reviewer-backend:latest 2>/dev/null || true
        docker rmi aicode-reviewer-frontend:latest 2>/dev/null || true
        
        print_success "Custom images removed"
    fi
}

# Function to cleanup system
cleanup_system() {
    if [[ "$1" == "--cleanup" ]] || [[ "$1" == "-c" ]]; then
        print_status "Cleaning up Docker system..."
        
        # Remove unused containers, networks, images
        docker system prune -f
        
        print_success "System cleanup completed"
    fi
}

# Function to show remaining resources
show_remaining() {
    echo ""
    print_status "Remaining Docker resources:"
    
    # Check for running containers
    local running_containers=$(docker ps --filter "name=aicode-reviewer" --format "table {{.Names}}\t{{.Status}}")
    if [[ -n "$running_containers" ]] && [[ "$running_containers" != "NAMES	STATUS" ]]; then
        echo "🔄 Running containers:"
        echo "$running_containers"
    else
        print_success "No running AI Code Reviewer containers"
    fi
    
    # Check for volumes
    local volumes=$(docker volume ls --filter "name=aicode-reviewer" --format "table {{.Name}}")
    if [[ -n "$volumes" ]] && [[ "$volumes" != "VOLUME NAME" ]]; then
        echo ""
        echo "💾 Data volumes:"
        echo "$volumes"
    fi
    
    # Check for images
    local images=$(docker images --filter "reference=aicode-reviewer*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}")
    if [[ -n "$images" ]] && [[ "$images" != "REPOSITORY	TAG	SIZE" ]]; then
        echo ""
        echo "🖼️  Images:"
        echo "$images"
    fi
}

# Main execution
main() {
    local remove_volumes_flag=false
    local remove_images_flag=false
    local cleanup_flag=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --volumes|-v)
                remove_volumes_flag=true
                shift
                ;;
            --images|-i)
                remove_images_flag=true
                shift
                ;;
            --cleanup|-c)
                cleanup_flag=true
                shift
                ;;
            --all|-a)
                remove_volumes_flag=true
                remove_images_flag=true
                cleanup_flag=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --volumes, -v   Remove data volumes (WARNING: deletes all data)"
                echo "  --images, -i    Remove custom Docker images"
                echo "  --cleanup, -c   Clean up Docker system (remove unused resources)"
                echo "  --all, -a       Combination of --volumes --images --cleanup"
                echo "  --help, -h      Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0                    # Stop services only"
                echo "  $0 --volumes          # Stop services and remove data"
                echo "  $0 --all              # Complete cleanup"
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
    check_docker_compose
    stop_services
    
    if [[ "$remove_volumes_flag" == "true" ]]; then
        remove_volumes --volumes
    fi
    
    if [[ "$remove_images_flag" == "true" ]]; then
        remove_images --images
    fi
    
    if [[ "$cleanup_flag" == "true" ]]; then
        cleanup_system --cleanup
    fi
    
    show_remaining
    
    echo ""
    print_success "🎉 Services stopped successfully!"
    echo ""
    echo "📋 To start services again:"
    echo "  ./scripts/start-services.sh"
    echo ""
    echo "📋 To start with fresh data:"
    echo "  ./scripts/start-services.sh"
    echo "  ./scripts/init-database.sh --reset"
}

# Run main function
main "$@" 