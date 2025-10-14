#!/bin/bash

# OmniFy Cloud Connect - Professional Deployment Script
# This script provides easy deployment options for different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
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

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE} $1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command_exists git; then
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_status "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to setup environment
setup_environment() {
    print_header "Setting Up Environment"
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            print_status "Creating .env file from env.example..."
            cp env.example .env
            print_warning "Please edit .env file with your actual API keys and credentials"
            print_status "You can use the following command to edit:"
            echo "  nano .env"
            echo ""
            print_status "Press Enter when you're ready to continue..."
            read -r
        else
            print_error "No env.example file found. Please create a .env file manually."
            exit 1
        fi
    else
        print_success ".env file already exists"
    fi
}

# Function to generate secure passwords
generate_passwords() {
    print_header "Generating Secure Passwords"
    
    # Generate secure passwords if not set
    if ! grep -q "MONGO_ROOT_PASSWORD=your_secure_password_here" .env; then
        print_success "MongoDB password already configured"
    else
        MONGO_PASS=$(openssl rand -base64 32)
        sed -i "s/MONGO_ROOT_PASSWORD=your_secure_password_here/MONGO_ROOT_PASSWORD=$MONGO_PASS/" .env
        print_success "Generated secure MongoDB password"
    fi
    
    if ! grep -q "REDIS_PASSWORD=your_redis_password_here" .env; then
        print_success "Redis password already configured"
    else
        REDIS_PASS=$(openssl rand -base64 32)
        sed -i "s/REDIS_PASSWORD=your_redis_password_here/REDIS_PASSWORD=$REDIS_PASS/" .env
        print_success "Generated secure Redis password"
    fi
    
    if ! grep -q "JWT_SECRET_KEY=your_jwt_secret_key_minimum_32_characters_long" .env; then
        print_success "JWT secret already configured"
    else
        JWT_SECRET=$(openssl rand -base64 48)
        sed -i "s/JWT_SECRET_KEY=your_jwt_secret_key_minimum_32_characters_long/JWT_SECRET_KEY=$JWT_SECRET/" .env
        print_success "Generated secure JWT secret"
    fi
}

# Function to deploy development environment
deploy_development() {
    print_header "Deploying Development Environment"
    
    print_status "Building and starting services..."
    docker-compose up --build -d
    
    print_status "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend service is healthy"
    else
        print_warning "Backend service may still be starting up"
    fi
    
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend service is healthy"
    else
        print_warning "Frontend service may still be starting up"
    fi
    
    print_success "Development environment deployed successfully!"
    print_status "Access your application at:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Grafana: http://localhost:3001 (admin/admin)"
    echo "  Prometheus: http://localhost:9090"
}

# Function to deploy production environment
deploy_production() {
    print_header "Deploying Production Environment"
    
    print_warning "Production deployment requires additional configuration:"
    print_status "1. SSL certificates"
    print_status "2. Domain configuration"
    print_status "3. Production API keys"
    print_status "4. Database backups"
    print_status "5. Monitoring setup"
    echo ""
    
    read -p "Do you want to continue with production deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Production deployment cancelled"
        exit 0
    fi
    
    print_status "Building production images..."
    docker-compose -f docker-compose.prod.yml build
    
    print_status "Starting production services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Production environment deployed!"
    print_status "Make sure to configure your reverse proxy and SSL certificates"
}

# Function to run tests
run_tests() {
    print_header "Running Tests"
    
    print_status "Running backend tests..."
    docker-compose exec backend python -m pytest tests/ -v
    
    print_status "Running frontend tests..."
    docker-compose exec frontend npm test -- --coverage --watchAll=false
    
    print_success "All tests completed!"
}

# Function to show logs
show_logs() {
    print_header "Showing Service Logs"
    
    echo "Select service to view logs:"
    echo "1) Backend"
    echo "2) Frontend"
    echo "3) MongoDB"
    echo "4) Redis"
    echo "5) All services"
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1) docker-compose logs -f backend ;;
        2) docker-compose logs -f frontend ;;
        3) docker-compose logs -f mongodb ;;
        4) docker-compose logs -f redis ;;
        5) docker-compose logs -f ;;
        *) print_error "Invalid choice" ;;
    esac
}

# Function to stop services
stop_services() {
    print_header "Stopping Services"
    
    docker-compose down
    print_success "All services stopped"
}

# Function to clean up
cleanup() {
    print_header "Cleaning Up"
    
    print_warning "This will remove all containers, volumes, and images. Are you sure?"
    read -p "Type 'yes' to confirm: " confirmation
    
    if [ "$confirmation" = "yes" ]; then
        docker-compose down -v --rmi all
        docker system prune -f
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to show status
show_status() {
    print_header "Service Status"
    
    docker-compose ps
    
    echo ""
    print_status "Service Health Checks:"
    
    # Check backend
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "✓ Backend API (http://localhost:8000)"
    else
        print_error "✗ Backend API (http://localhost:8000)"
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        print_success "✓ Frontend (http://localhost:3000)"
    else
        print_error "✗ Frontend (http://localhost:3000)"
    fi
    
    # Check MongoDB
    if docker-compose exec mongodb mongosh --eval "db.runCommand('ping')" >/dev/null 2>&1; then
        print_success "✓ MongoDB"
    else
        print_error "✗ MongoDB"
    fi
    
    # Check Redis
    if docker-compose exec redis redis-cli ping >/dev/null 2>&1; then
        print_success "✓ Redis"
    else
        print_error "✗ Redis"
    fi
}

# Function to backup data
backup_data() {
    print_header "Backing Up Data"
    
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    print_status "Creating MongoDB backup..."
    docker-compose exec mongodb mongodump --out /tmp/backup
    docker cp "$(docker-compose ps -q mongodb):/tmp/backup" "$backup_dir/mongodb"
    
    print_status "Creating Redis backup..."
    docker-compose exec redis redis-cli BGSAVE
    docker cp "$(docker-compose ps -q redis):/data/dump.rdb" "$backup_dir/redis/"
    
    print_success "Backup completed: $backup_dir"
}

# Function to restore data
restore_data() {
    print_header "Restoring Data"
    
    echo "Available backups:"
    ls -la backups/
    
    read -p "Enter backup directory name: " backup_name
    
    if [ ! -d "backups/$backup_name" ]; then
        print_error "Backup directory not found"
        exit 1
    fi
    
    print_warning "This will overwrite existing data. Are you sure?"
    read -p "Type 'yes' to confirm: " confirmation
    
    if [ "$confirmation" = "yes" ]; then
        print_status "Restoring MongoDB..."
        docker-compose exec mongodb mongorestore /tmp/backup
        
        print_status "Restoring Redis..."
        docker cp "backups/$backup_name/redis/dump.rdb" "$(docker-compose ps -q redis):/data/"
        docker-compose restart redis
        
        print_success "Data restored from backup: $backup_name"
    else
        print_status "Restore cancelled"
    fi
}

# Main menu
show_menu() {
    echo ""
    print_header "OmniFy Cloud Connect Deployment"
    echo ""
    echo "1) Deploy Development Environment"
    echo "2) Deploy Production Environment"
    echo "3) Run Tests"
    echo "4) Show Service Status"
    echo "5) Show Logs"
    echo "6) Stop Services"
    echo "7) Backup Data"
    echo "8) Restore Data"
    echo "9) Cleanup (Remove All)"
    echo "0) Exit"
    echo ""
}

# Main script
main() {
    print_header "OmniFy Cloud Connect - Professional Deployment"
    echo ""
    print_status "Welcome to OmniFy Cloud Connect deployment script!"
    print_status "This script will help you deploy and manage your OmniFy instance."
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Setup environment
    setup_environment
    
    # Generate passwords
    generate_passwords
    
    while true; do
        show_menu
        read -p "Enter your choice (0-9): " choice
        
        case $choice in
            1) deploy_development ;;
            2) deploy_production ;;
            3) run_tests ;;
            4) show_status ;;
            5) show_logs ;;
            6) stop_services ;;
            7) backup_data ;;
            8) restore_data ;;
            9) cleanup ;;
            0) 
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please try again."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main "$@"
