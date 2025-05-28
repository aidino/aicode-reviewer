#!/bin/bash

# AI Code Reviewer - Database Initialization Script
# Khởi tạo và reset database (PostgreSQL + Neo4j)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗄️ AI Code Reviewer - Database Initialization${NC}"
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

# Function to check if Docker containers are running
check_containers() {
    print_status "Checking if database containers are running..."
    
    if ! docker ps | grep -q "aicode-reviewer-postgres"; then
        print_error "PostgreSQL container is not running. Please start services first: ./scripts/start-services.sh"
        exit 1
    fi
    
    if ! docker ps | grep -q "aicode-reviewer-neo4j"; then
        print_error "Neo4j container is not running. Please start services first: ./scripts/start-services.sh"
        exit 1
    fi
    
    print_success "Database containers are running"
}

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
    print_status "Waiting for PostgreSQL to be ready..."
    
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if docker exec aicode-reviewer-postgres pg_isready -U aicode >/dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "PostgreSQL is not responding after $max_attempts attempts"
    exit 1
}

# Function to wait for Neo4j to be ready
wait_for_neo4j() {
    print_status "Waiting for Neo4j to be ready..."
    
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if docker exec aicode-reviewer-neo4j cypher-shell "RETURN 1" >/dev/null 2>&1; then
            print_success "Neo4j is ready"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "Neo4j is not responding after $max_attempts attempts"
    exit 1
}

# Function to create PostgreSQL database if not exists
create_postgres_database() {
    print_status "Creating PostgreSQL database if not exists..."
    
    # Check if database exists
    local db_exists=$(docker exec aicode-reviewer-postgres psql -U aicode -lqt | cut -d \| -f 1 | grep -w aicode_reviewer && echo "yes" || echo "no")
    
    if [[ "$db_exists" == "no" ]]; then
        print_status "Creating database 'aicode_reviewer'..."
        docker exec aicode-reviewer-postgres createdb -U aicode aicode_reviewer
        print_success "Database created"
    else
        print_success "Database 'aicode_reviewer' already exists"
    fi
    
    # Enable pgvector extension
    print_status "Enabling pgvector extension..."
    docker exec aicode-reviewer-postgres psql -U aicode -d aicode_reviewer -c "CREATE EXTENSION IF NOT EXISTS vector;"
    print_success "pgvector extension enabled"
}

# Function to run Alembic migrations
run_migrations() {
    print_status "Running database migrations with Alembic..."
    
    # Check if backend container is running
    if docker ps | grep -q "aicode-reviewer-backend"; then
        # Run migrations from backend container
        docker exec aicode-reviewer-backend alembic upgrade head
        print_success "Migrations completed via backend container"
    else
        # Run migrations from local environment
        print_status "Backend container not running, running migrations locally..."
        
        # Change to backend directory
        cd src/webapp/backend
        
        # Check if virtual environment exists
        if [[ -d "../../../venv" ]]; then
            source ../../../venv/bin/activate
            print_success "Activated virtual environment"
        else
            print_warning "Virtual environment not found. Using system Python."
        fi
        
        # Set environment variables for local run
        export POSTGRES_HOST=localhost
        export POSTGRES_PORT=5432
        export POSTGRES_USER=aicode
        export POSTGRES_PASSWORD=aicode123
        export POSTGRES_DB=aicode_reviewer
        
        # Run migrations
        alembic upgrade head
        print_success "Migrations completed locally"
        
        # Return to root directory
        cd ../../..
    fi
}

# Function to create initial database revision if not exists
create_initial_migration() {
    print_status "Checking for initial migration..."
    
    local migrations_dir="src/webapp/backend/alembic/versions"
    
    if [[ ! -d "$migrations_dir" ]] || [[ -z "$(ls -A $migrations_dir 2>/dev/null)" ]]; then
        print_status "No migrations found. Creating initial migration..."
        
        cd src/webapp/backend
        
        if [[ -d "../../../venv" ]]; then
            source ../../../venv/bin/activate
        fi
        
        # Set environment variables
        export POSTGRES_HOST=localhost
        export POSTGRES_PORT=5432
        export POSTGRES_USER=aicode
        export POSTGRES_PASSWORD=aicode123
        export POSTGRES_DB=aicode_reviewer
        
        # Create initial migration
        alembic revision --autogenerate -m "Initial migration with authentication tables"
        print_success "Initial migration created"
        
        cd ../../..
    else
        print_success "Migrations already exist"
    fi
}

# Function to seed initial data
seed_initial_data() {
    print_status "Seeding initial data..."
    
    # Create initial data SQL
    local init_sql="
-- Insert default user role if not exists
INSERT INTO user_roles (name, description) 
VALUES ('admin', 'Administrator role'), ('user', 'Regular user role')
ON CONFLICT (name) DO NOTHING;

-- Insert default admin user if not exists
INSERT INTO users (username, email, password_hash, role, is_active, created_at, updated_at)
VALUES ('admin', 'admin@aicode-reviewer.com', '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin', true, NOW(), NOW())
ON CONFLICT (username) DO NOTHING;

-- Insert admin profile
INSERT INTO user_profiles (user_id, full_name, timezone, preferences, created_at, updated_at)
SELECT u.id, 'System Administrator', 'UTC', '{}', NOW(), NOW()
FROM users u 
WHERE u.username = 'admin' 
AND NOT EXISTS (SELECT 1 FROM user_profiles WHERE user_id = u.id);
"
    
    # Execute SQL
    docker exec aicode-reviewer-postgres psql -U aicode -d aicode_reviewer -c "$init_sql"
    print_success "Initial data seeded (admin user: admin / password: secret)"
}

# Function to initialize Neo4j
init_neo4j() {
    print_status "Initializing Neo4j knowledge graph..."
    
    # Create constraints and indexes
    local neo4j_init="
CREATE CONSTRAINT unique_file_path IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE;
CREATE CONSTRAINT unique_class_name IF NOT EXISTS FOR (c:Class) REQUIRE (c.name, c.file_path) IS UNIQUE;
CREATE CONSTRAINT unique_function_name IF NOT EXISTS FOR (fn:Function) REQUIRE (fn.name, fn.class_name, fn.file_path) IS UNIQUE;
CREATE CONSTRAINT unique_variable_name IF NOT EXISTS FOR (v:Variable) REQUIRE (v.name, v.scope, v.file_path) IS UNIQUE;

CREATE INDEX file_language_idx IF NOT EXISTS FOR (f:File) ON (f.language);
CREATE INDEX class_type_idx IF NOT EXISTS FOR (c:Class) ON (c.type);
CREATE INDEX function_type_idx IF NOT EXISTS FOR (fn:Function) ON (fn.type);
CREATE INDEX variable_type_idx IF NOT EXISTS FOR (v:Variable) ON (v.type);

// Create sample knowledge graph structure
MERGE (kg:KnowledgeGraph {name: 'AI Code Reviewer', created_at: datetime()})
SET kg.updated_at = datetime();
"
    
    docker exec aicode-reviewer-neo4j cypher-shell -u neo4j -p password "$neo4j_init"
    print_success "Neo4j knowledge graph initialized"
}

# Function to verify database setup
verify_setup() {
    print_status "Verifying database setup..."
    
    # Check PostgreSQL tables
    local pg_tables=$(docker exec aicode-reviewer-postgres psql -U aicode -d aicode_reviewer -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    print_status "PostgreSQL tables: $(echo $pg_tables | tr -d ' ')"
    
    # Check Neo4j nodes
    local neo4j_nodes=$(docker exec aicode-reviewer-neo4j cypher-shell -u neo4j -p password "MATCH (n) RETURN count(n)" --format plain | tail -n 1)
    print_status "Neo4j nodes: $(echo $neo4j_nodes | tr -d ' ')"
    
    # Test database connections
    if docker exec aicode-reviewer-postgres psql -U aicode -d aicode_reviewer -c "SELECT 1;" >/dev/null 2>&1; then
        print_success "PostgreSQL connection: OK"
    else
        print_error "PostgreSQL connection: FAILED"
    fi
    
    if docker exec aicode-reviewer-neo4j cypher-shell -u neo4j -p password "RETURN 1" >/dev/null 2>&1; then
        print_success "Neo4j connection: OK"
    else
        print_error "Neo4j connection: FAILED"
    fi
}

# Function to reset databases
reset_databases() {
    print_warning "This will delete ALL data in the databases. Are you sure? (y/N)"
    read -r confirmation
    
    if [[ "$confirmation" =~ ^[Yy]$ ]]; then
        print_status "Resetting databases..."
        
        # Reset PostgreSQL
        print_status "Dropping and recreating PostgreSQL database..."
        docker exec aicode-reviewer-postgres dropdb -U aicode --if-exists aicode_reviewer
        docker exec aicode-reviewer-postgres createdb -U aicode aicode_reviewer
        docker exec aicode-reviewer-postgres psql -U aicode -d aicode_reviewer -c "CREATE EXTENSION IF NOT EXISTS vector;"
        
        # Reset Neo4j
        print_status "Clearing Neo4j database..."
        docker exec aicode-reviewer-neo4j cypher-shell -u neo4j -p password "MATCH (n) DETACH DELETE n"
        
        print_success "Databases reset successfully"
        
        # Re-run initialization
        create_initial_migration
        run_migrations
        seed_initial_data
        init_neo4j
        
        print_success "Databases re-initialized after reset"
    else
        print_status "Reset cancelled"
    fi
}

# Function to show database info
show_database_info() {
    echo ""
    print_status "Database Information:"
    echo "📊 PostgreSQL:"
    echo "   Host: localhost:5432"
    echo "   Database: aicode_reviewer"
    echo "   User: aicode"
    echo "   Password: aicode123"
    echo ""
    echo "🕸️  Neo4j:"
    echo "   HTTP: http://localhost:7474"
    echo "   Bolt: bolt://localhost:7687"
    echo "   User: neo4j"
    echo "   Password: password"
    echo ""
    echo "👤 Default Admin User:"
    echo "   Username: admin"
    echo "   Password: secret"
    echo "   Email: admin@aicode-reviewer.com"
}

# Main execution
main() {
    local reset_mode=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --reset|-r)
                reset_mode=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --reset, -r    Reset all databases (WARNING: deletes all data)"
                echo "  --help, -h     Show this help message"
                echo ""
                echo "This script initializes PostgreSQL and Neo4j databases for AI Code Reviewer."
                echo "Make sure to start services first with: ./scripts/start-services.sh"
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
    check_containers
    wait_for_postgres
    wait_for_neo4j
    
    if [[ "$reset_mode" == "true" ]]; then
        reset_databases
    else
        create_postgres_database
        create_initial_migration
        run_migrations
        seed_initial_data
        init_neo4j
    fi
    
    verify_setup
    show_database_info
    
    echo ""
    print_success "🎉 Database initialization completed!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Access frontend: http://localhost:5173"
    echo "  2. Login with admin/secret"
    echo "  3. Access Neo4j browser: http://localhost:7474"
    echo "  4. Check API docs: http://localhost:8000/docs"
}

# Run main function
main "$@" 