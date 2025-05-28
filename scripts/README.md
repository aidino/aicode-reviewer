# AI Code Reviewer - Scripts Documentation

Thư mục này chứa các scripts để quản lý và khởi chạy AI Code Reviewer system.

## 📋 Tổng quan Scripts

### 🎯 Master Control Script
- **`aicode-reviewer`** - Script CLI tổng hợp để quản lý toàn bộ hệ thống

### 🚀 Service Management Scripts  
- **`start-services.sh`** - Khởi chạy toàn bộ services với Docker Compose
- **`stop-services.sh`** - Dừng services và cleanup Docker resources
- **`init-database.sh`** - Khởi tạo và reset databases (PostgreSQL + Neo4j)

### 🛠️ Legacy Scripts (Có sẵn)
- **`start_infrastructure.sh`** - Script khởi chạy infrastructure cũ
- **`start_dev_servers.py`** - Python script để start development servers
- **`check_logs.py`** - Utility để kiểm tra logs

## 🎮 Master Control Script Usage

Script `aicode-reviewer` là interface chính để quản lý toàn bộ hệ thống:

### Khởi chạy nhanh (Quick Start)
```bash
# Start development environment
./scripts/aicode-reviewer dev

# Hoặc step-by-step
./scripts/aicode-reviewer start --build
./scripts/aicode-reviewer init-db
```

### Service Management
```bash
# Start all services
./scripts/aicode-reviewer start                    # Basic start
./scripts/aicode-reviewer start --build            # Start with fresh build  
./scripts/aicode-reviewer start --build --logs     # Start, build và follow logs

# Stop services
./scripts/aicode-reviewer stop                     # Stop services only
./scripts/aicode-reviewer stop --volumes           # Stop và remove data volumes
./scripts/aicode-reviewer stop --all               # Complete cleanup

# Restart services
./scripts/aicode-reviewer restart                  # Basic restart
./scripts/aicode-reviewer restart --build          # Restart with fresh build

# Check status
./scripts/aicode-reviewer status                   # Show service status và health

# View logs  
./scripts/aicode-reviewer logs                     # All service logs
./scripts/aicode-reviewer logs backend             # Specific service logs
./scripts/aicode-reviewer logs frontend            # Frontend logs only
```

### Database Management
```bash
# Initialize databases
./scripts/aicode-reviewer init-db                  # Setup PostgreSQL + Neo4j

# Reset databases (WARNING: deletes all data)
./scripts/aicode-reviewer reset-db                 # Complete database reset
```

### Development & Testing
```bash
# Build images
./scripts/aicode-reviewer build                    # Build custom images
./scripts/aicode-reviewer build --no-cache         # Force rebuild without cache

# Run tests
./scripts/aicode-reviewer test                     # All tests
./scripts/aicode-reviewer test auth                # Authentication tests only
./scripts/aicode-reviewer test backend             # Backend tests only  
./scripts/aicode-reviewer test frontend            # Frontend tests only

# Clean up
./scripts/aicode-reviewer clean                    # Basic Docker cleanup
./scripts/aicode-reviewer clean --all              # Complete cleanup với volumes
```

## 🔧 Individual Scripts Usage

### start-services.sh
Khởi chạy toàn bộ services với Docker Compose:

```bash
# Basic usage
./scripts/start-services.sh

# Options
./scripts/start-services.sh --build                # Force rebuild images
./scripts/start-services.sh --pull                 # Pull latest base images
./scripts/start-services.sh --logs                 # Follow logs after start
./scripts/start-services.sh --build --logs         # Build + follow logs
```

**Features:**
- ✅ Automatic Docker và Docker Compose detection
- ✅ Environment file creation (.env) nếu không tồn tại
- ✅ Required directories creation
- ✅ Health checks cho tất cả services
- ✅ Service status display với URLs
- ✅ Comprehensive error handling

### stop-services.sh
Dừng services và cleanup Docker resources:

```bash
# Basic usage
./scripts/stop-services.sh

# Options
./scripts/stop-services.sh --volumes               # Remove data volumes
./scripts/stop-services.sh --images                # Remove custom images
./scripts/stop-services.sh --cleanup               # Docker system cleanup
./scripts/stop-services.sh --all                   # Complete cleanup
```

**Features:**
- ✅ Graceful service shutdown
- ✅ Optional data volume removal với confirmation
- ✅ Custom image cleanup
- ✅ Docker system pruning
- ✅ Resource usage display

### init-database.sh
Khởi tạo và quản lý databases:

```bash
# Basic usage
./scripts/init-database.sh

# Reset databases (WARNING: deletes data)
./scripts/init-database.sh --reset
```

**Features:**
- ✅ PostgreSQL database creation và pgvector extension
- ✅ Alembic migrations (từ container hoặc local)
- ✅ Initial data seeding (admin user: admin/secret)
- ✅ Neo4j knowledge graph initialization  
- ✅ Database connection verification
- ✅ Complete reset functionality

## 🌐 Service URLs

Sau khi khởi chạy thành công, các services sẽ available tại:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | React development server |
| **Backend API** | http://localhost:8000 | FastAPI server |
| **API Documentation** | http://localhost:8000/docs | OpenAPI/Swagger docs |
| **Neo4j Browser** | http://localhost:7474 | Neo4j web interface |
| **PostgreSQL** | localhost:5432 | Database server |
| **Redis** | localhost:6379 | Cache server |

## 🔐 Default Credentials

### Admin User (Web Interface)
- **Username:** `admin`
- **Password:** `secret`
- **Email:** `admin@aicode-reviewer.com`

### Database Credentials
- **PostgreSQL:**
  - Host: `localhost:5432`
  - Database: `aicode_reviewer`
  - User: `aicode`
  - Password: `aicode123`

- **Neo4j:**
  - HTTP: `http://localhost:7474`
  - Bolt: `bolt://localhost:7687`
  - User: `neo4j`
  - Password: `password`

## 🐳 Docker Services

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │     Backend     │    │     Neo4j       │
│   (React/Vite)  │    │   (FastAPI)     │    │ (Knowledge DB)  │
│   Port: 5173    │────│   Port: 8000    │────│   Port: 7474    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              │
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │
│  (Vector DB)    │    │   (Cache)       │
│   Port: 5432    │────│   Port: 6379    │
└─────────────────┘    └─────────────────┘
```

### Health Checks
Tất cả services đều có health checks để đảm bảo stability:
- **PostgreSQL:** `pg_isready` command
- **Neo4j:** Cypher query execution  
- **Redis:** `PING` command
- **Backend:** HTTP health endpoint `/health`
- **Frontend:** HTTP availability check

## 🔧 Development Workflow

### First Time Setup
```bash
# 1. Start development environment
./scripts/aicode-reviewer dev

# 2. Verify services
./scripts/aicode-reviewer status

# 3. Access applications
open http://localhost:5173    # Frontend
open http://localhost:8000/docs   # API docs
```

### Daily Development
```bash
# Start development
./scripts/aicode-reviewer start

# View logs during development
./scripts/aicode-reviewer logs

# Run tests
./scripts/aicode-reviewer test auth

# Stop when done
./scripts/aicode-reviewer stop
```

### Troubleshooting
```bash
# Check service status
./scripts/aicode-reviewer status

# View specific service logs
./scripts/aicode-reviewer logs backend
./scripts/aicode-reviewer logs frontend

# Restart with fresh build
./scripts/aicode-reviewer restart --build

# Complete reset if needed
./scripts/aicode-reviewer stop --all
./scripts/aicode-reviewer start --build
./scripts/aicode-reviewer reset-db
```

## 📝 Environment Configuration

### .env File
Scripts tự động tạo `.env` file với default values:

```bash
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
```

### Production Configuration
Cho production deployment, update các values sau trong `.env`:
- `JWT_SECRET_KEY` - Generate secure random key
- `POSTGRES_PASSWORD` - Strong database password  
- `NEO4J_PASSWORD` - Strong Neo4j password
- `API_DEBUG=false` - Disable debug mode
- LLM API keys cho actual AI functionality

## 🧪 Testing Integration

Scripts tích hợp với testing framework:

### Authentication Tests
```bash
./scripts/aicode-reviewer test auth
# Runs: src/webapp/frontend/scripts/test-auth.sh
```

### Backend Tests  
```bash
./scripts/aicode-reviewer test backend
# Runs: pytest tests/webapp/backend/ -v
```

### Frontend Tests
```bash
./scripts/aicode-reviewer test frontend  
# Runs: npm test in frontend directory
```

### All Tests
```bash
./scripts/aicode-reviewer test
# Runs all test suites sequentially
```

## 🚨 Troubleshooting Common Issues

### Docker Issues
```bash
# Docker not running
sudo systemctl start docker

# Permission issues
sudo usermod -aG docker $USER
newgrp docker

# Port conflicts
./scripts/aicode-reviewer stop --all
# Change ports in docker-compose.yml if needed
```

### Database Issues
```bash
# Database connection failures
./scripts/aicode-reviewer logs postgres
./scripts/aicode-reviewer logs neo4j

# Reset databases
./scripts/aicode-reviewer reset-db
```

### Build Issues
```bash
# Clear Docker cache
./scripts/aicode-reviewer build --no-cache

# Complete cleanup và rebuild
./scripts/aicode-reviewer clean --all
./scripts/aicode-reviewer start --build
```

### Service Health Issues
```bash
# Check individual service status
./scripts/aicode-reviewer status

# View service logs
./scripts/aicode-reviewer logs [service_name]

# Restart specific service
docker compose restart [service_name]
```

## 📚 References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL + pgvector](https://github.com/pgvector/pgvector)
- [Neo4j Docker](https://neo4j.com/docs/operations-manual/current/docker/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)

---

**Note:** Tất cả scripts được thiết kế để idempotent và safe để chạy multiple times. Chúng sẽ check existing state và chỉ thực hiện necessary changes. 