# **AI-Powered In-Depth Code Review System**

## **Project Overview**

This project aims to develop a sophisticated, AI-driven system for in-depth code review. Leveraging Large Language Models (LLMs) and Abstract Syntax Tree (AST) analysis, the system is designed to provide deep semantic understanding of code changes, identify potential issues, and offer actionable solutions. It supports on-demand scanning for both individual Pull Requests (PRs) and entire projects.

The core mission is to significantly improve code quality, enhance developer productivity, and maintain the integrity of software architecture. By offering comprehensive, automated analysis, the system helps in proactively identifying risks, reducing technical debt, and accelerating development cycles.

## **Key Features**

* **Deep Semantic Analysis:** Utilizes LLMs for a nuanced understanding of code logic, intent, and potential bugs beyond simple static checks.  
* **Hybrid Analysis Model:** Combines the structural precision of AST-based analysis with the contextual understanding of LLMs and Retrieval Augmented Generation (RAG).  
* **Multi-Agent Architecture:** Employs a system of specialized AI agents (orchestrated by LangGraph) to handle distinct tasks in the review process, such as code fetching, parsing, static analysis, impact analysis, LLM interaction, and report generation.  
* **Interactive Web Application:** Modern React-based frontend with interactive diagram visualization, zoom/pan capabilities, and specialized language viewers.
* **Agent Workflow Visualization:** Real-time interactive visualization of multi-agent workflow with React Flow, WebSocket updates, status tracking, and detailed agent insights.
* **Enhanced XAI Solution Suggestions:** Advanced solution suggestion engine with explainable AI capabilities, multiple alternatives analysis, confidence scoring, evidence-based reasoning, and comprehensive error handling.
* **Actionable Error Resolution:** Focuses on generating clear, context-aware, and practical suggestions to help developers easily fix identified issues.  
* **Advanced Diagram Generation:** Generates interactive class diagrams and sequence diagrams (using PlantUML/Mermaid.js) with timeline navigation and export capabilities.
* **Multi-Language Support:** Python, Java, Kotlin (including Android-specific analysis) with language-specific report viewers.
* **Real-time Scan Processing:** Async scan initiation with progress tracking and task management.
* **On-Demand Scanning:** Allows users (developers, tech leads) to initiate scans for specific PRs (open or closed) or entire projects as needed.  
* **Comprehensive Reporting:** Produces detailed reports with interactive visualization, filtering, and export capabilities.
* **Enterprise Authentication System:** Complete JWT-based authentication with user management, role-based access control, session management, rate limiting, and comprehensive security headers.
* **Standalone & Self-Hosted:** Designed to operate as an independent tool, self-hosted by the user to ensure data privacy and control over proprietary code.  
* **Open Source Prioritization:** Built with a strong preference for open-source technologies and components.
* **Change Impact Analysis:** Phân tích tác động của thay đổi mã nguồn (ImpactAnalysisAgent) giúp xác định các file, class, function bị ảnh hưởng trực tiếp/gián tiếp bởi diff hoặc PR, hỗ trợ đánh giá rủi ro lan truyền và ưu tiên review.

### **🎯 Enhanced Solution Suggestion Agent**

The system now features an **advanced Enhanced Solution Suggestion Agent** with cutting-edge XAI (Explainable AI) capabilities:

#### **Core XAI Features**
- **Explainable Reasoning**: Detailed explanations for why solutions are recommended with confidence scoring
- **Evidence-Based Analysis**: Supporting evidence from best practices, security principles, and performance benchmarks
- **Multiple Solution Alternatives**: Up to 3 different approaches with comprehensive pros/cons analysis
- **Confidence Tracking**: Numerical confidence scores (0.0-1.0) with human-readable confidence levels

#### **Advanced Capabilities**
- **Diverse Suggestion Types**: Security fixes, performance optimizations, best practices, bug fixes, testing improvements, architecture recommendations
- **Context-Specific Prompts**: Tailored prompts based on finding type (security, performance, etc.)
- **Comprehensive Error Handling**: Graceful fallback mechanisms for LLM timeouts, network errors, and malformed responses
- **Performance Metrics**: Real-time tracking of generation times, success rates, and quality metrics

#### **Solution Quality Features**
- **Implementation Complexity Assessment**: Low/medium/high complexity ratings with effort estimates
- **Impact Analysis**: Detailed assessment of potential impact if solutions are applied
- **Step-by-Step Guidance**: Clear implementation steps and best practice recommendations
- **Risk Assessment**: Comprehensive risk analysis for each proposed solution

#### **Production-Ready Reliability**
- **Batch Processing**: Efficient processing of multiple findings with metrics tracking
- **Unicode Support**: Full support for international characters and emojis in code
- **Memory Management**: Optimized for large codebases and complex analysis
- **Comprehensive Testing**: 39 test cases covering normal operations, edge cases, and error scenarios

### **🔐 Enterprise Authentication System**

The system includes a comprehensive, production-ready authentication system with enterprise-grade security features:

#### **Core Authentication Features**
- **JWT-Based Authentication**: Secure token-based authentication with access and refresh tokens
- **User Management**: Complete user registration, login, logout, and profile management
- **Role-Based Access Control**: Support for ADMIN, USER, and GUEST roles with granular permissions
- **Session Management**: Advanced session tracking with device information and IP logging
- **Password Security**: Bcrypt hashing with configurable complexity and strength validation

#### **Security Enhancements**
- **Rate Limiting**: Intelligent rate limiting to prevent brute force attacks on auth endpoints
- **Token Blacklisting**: Comprehensive token invalidation and session revocation
- **Security Headers**: Full suite of security headers (HSTS, CSP, X-Frame-Options, etc.)
- **CORS Configuration**: Configurable CORS policies for development and production environments
- **Input Validation**: Comprehensive request validation with Pydantic schemas

#### **Advanced Features**
- **Multi-Session Support**: Users can manage multiple active sessions across devices
- **Session Analytics**: Track login history, device information, and session activity
- **Automatic Cleanup**: Intelligent cleanup of expired sessions and tokens
- **Development/Production Modes**: Separate security configurations for different environments

#### **API Endpoints**
- `POST /auth/register` - User registration with validation
- `POST /auth/login` - User authentication with device tracking
- `POST /auth/logout` - Secure logout with token blacklisting
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update user profile
- `POST /auth/refresh` - Refresh access tokens
- `POST /auth/change-password` - Secure password changes
- `GET /auth/sessions` - List user sessions
- `DELETE /auth/sessions/{id}` - Revoke specific sessions

#### **Testing & Reliability**
- **Comprehensive Test Suite**: 60+ test cases covering all authentication scenarios
- **High Test Coverage**: 95%+ coverage on authentication utilities and models
- **Edge Case Handling**: Robust error handling for network issues, invalid tokens, and edge cases
- **Performance Testing**: Rate limiting and concurrent session testing

## **Strategic Value**

This system moves beyond traditional linters and basic static analysis tools by:

* Providing proactive and in-depth code quality assurance with interactive visualization.
* Offering insights into architectural health and potential risks through advanced diagramming.
* Reducing the manual effort in code reviews, allowing senior developers to focus on more complex design challenges.  
* Facilitating a culture of high-quality engineering and continuous improvement through accessible web interface.
* Supporting multi-language development teams with specialized analysis for Python, Java, and Kotlin.

## **Project Structure**

```
aicode-reviewer/
├── src/                           # Main source code
│   ├── core_engine/              # Core analysis engine
│   │   ├── agents/               # LangGraph agents (CodeFetcher, ASTParser, etc.)
│   │   ├── orchestrator.py       # Main workflow orchestration
│   │   ├── diagramming_engine.py # Diagram generation logic
│   │   ├── risk_predictor.py     # Risk prediction model
│   │   └── project_scanning_agent.py # Full project scanning
│   ├── webapp/                   # Web application
│   │   ├── backend/              # FastAPI backend
│   │   │   ├── api/              # API routes and endpoints
│   │   │   ├── auth/             # Authentication system
│   │   │   │   ├── models.py     # User, UserProfile, UserSession models
│   │   │   │   ├── utils.py      # JWT utilities, password hashing
│   │   │   │   ├── service.py    # Authentication business logic
│   │   │   │   ├── middleware.py # Auth middleware and decorators
│   │   │   │   ├── routes.py     # Auth API endpoints
│   │   │   │   ├── schemas.py    # Request/response schemas
│   │   │   │   ├── rate_limiting.py # Rate limiting for auth endpoints
│   │   │   │   └── security.py   # Security headers and CORS
│   │   │   ├── models/           # Pydantic data models
│   │   │   ├── services/         # Business logic services
│   │   │   ├── database.py       # Database configuration
│   │   │   └── alembic/          # Database migrations
│   │   └── frontend/             # React frontend
│   │       ├── src/              # Frontend source code
│   │       │   ├── components/   # React components
│   │       │   ├── pages/        # Page components
│   │       │   ├── services/     # API client services
│   │       │   └── types/        # TypeScript type definitions
│   │       ├── dist/             # Built frontend assets
│   │       └── e2e/              # End-to-end tests
│   ├── reporting/                # Report generation and formatting
│   ├── utils/                    # Utility functions and helpers
│   └── main.py                   # Application entry point
├── tests/                        # Unit tests mirroring src structure
│   ├── core_engine/              # Core engine tests
│   ├── webapp/backend/           # Backend API tests
│   │   ├── test_auth_models.py   # Authentication models tests
│   │   ├── test_auth_utils.py    # Authentication utilities tests
│   │   ├── test_auth_routes.py   # Authentication API tests
│   │   └── test_rate_limiting.py # Rate limiting tests
│   └── webapp/frontend/          # Frontend component tests
├── scripts/                      # Demo and utility scripts
├── docs/                         # Documentation (PLANNING.md, TASK.md)
├── config/                       # Configuration files and settings
├── requirements.txt              # Python dependencies
└── .env.example                 # Environment variables template
```

## **Setup and Installation**

### **Prerequisites**

- **Python 3.8+**: Core engine and backend API
- **Node.js 18+**: Frontend development and build
- **Git**: Repository interaction
- **Optional**: CUDA-compatible GPU for local LLM inference

### **Quick Start với Docker (Recommended)**

🎯 **Khởi chạy nhanh toàn bộ hệ thống:**

```bash
# 1. Clone repository
git clone <repository-url>
cd aicode-reviewer

# 2. Start development environment (all-in-one)
./scripts/aicode-reviewer dev
```

Lệnh này sẽ:
- ✅ Khởi chạy tất cả services (Frontend, Backend, PostgreSQL, Neo4j, Redis)
- ✅ Tự động tạo environment file (.env)
- ✅ Khởi tạo databases với sample data
- ✅ Setup admin user (admin/secret)

🌐 **Truy cập ứng dụng:**
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Neo4j Browser:** http://localhost:7474

### **Scripts Quản lý Hệ thống**

Tất cả các thao tác quản lý hệ thống thông qua script `aicode-reviewer`:

```bash
# Service Management
./scripts/aicode-reviewer start                    # Start all services
./scripts/aicode-reviewer stop                     # Stop all services
./scripts/aicode-reviewer restart --build          # Restart with fresh build
./scripts/aicode-reviewer status                   # Show service status
./scripts/aicode-reviewer logs                     # View all logs
./scripts/aicode-reviewer logs backend             # View specific service logs

# Database Management
./scripts/aicode-reviewer init-db                  # Initialize databases
./scripts/aicode-reviewer reset-db                 # Reset all data (WARNING!)

# Development & Testing
./scripts/aicode-reviewer test                     # Run all tests
./scripts/aicode-reviewer test auth                # Run auth tests only
./scripts/aicode-reviewer build                    # Build Docker images
./scripts/aicode-reviewer clean                    # Clean Docker resources

# Complete cleanup
./scripts/aicode-reviewer stop --all               # Stop + remove volumes
```

📚 **Chi tiết:** Xem [scripts/README.md](scripts/README.md) để hiểu đầy đủ về các scripts.

### **Manual Setup (Nếu không dùng Docker)**

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd aicode-reviewer
   ```

2. **Backend Setup:**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env file with your configuration
   ```

3. **Frontend Setup:**
   ```bash
   # Navigate to frontend directory
   cd src/webapp/frontend
   
   # Install Node.js dependencies
   npm install
   
   # Build frontend (optional, for production)
   npm run build
   ```

4. **Start Development Servers:**
   ```bash
   # Terminal 1: Start backend (from project root)
   python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000
   
   # Terminal 2: Start frontend (from src/webapp/frontend)
   cd src/webapp/frontend
   npm run dev
   ```

5. **Access the Application:**
   - Frontend: http://localhost:5173 (Vite dev server)
   - Backend API: http://localhost:8000 (FastAPI server)
   - API Documentation: http://localhost:8000/docs (Swagger UI)

### **Dependencies**

#### Backend Dependencies
- **LangChain & LangGraph**: Multi-agent orchestration framework
- **FastAPI**: Web API framework with automatic OpenAPI documentation
- **SQLAlchemy**: Modern ORM with async support for database operations
- **Alembic**: Database migration management
- **PostgreSQL/SQLite**: Primary database (PostgreSQL) with SQLite for testing
- **JWT & Security**: PyJWT, python-jose, passlib for authentication and security
- **Tree-sitter**: AST parsing for multiple programming languages (Python, Java, Kotlin)
- **GitPython**: Git repository interaction
- **Radon**: Code complexity metrics calculation
- **pytest**: Testing framework with async support and comprehensive coverage

#### Frontend Dependencies
- **React 18**: Modern React with concurrent features
- **TypeScript**: Type-safe JavaScript development
- **React Router**: Client-side routing
- **react-zoom-pan-pinch**: Interactive diagram zoom/pan functionality
- **Mermaid**: Diagram rendering library
- **Vite**: Fast build tool and dev server
- **Vitest**: Fast unit testing framework
- **Playwright**: End-to-end testing framework

## **Development Status**

This project is currently at **Milestone 3.5 COMPLETED** - a fully functional web application with interactive features.

### **✅ Completed Milestones**

- **[✅] Milestone 1**: Proof-of-Concept Core Engine & Single Language (Python)
- **[✅] Milestone 2.5**: Basic Java Support with AST parsing and static analysis
- **[✅] Milestone 2.6**: Commercial LLM APIs Integration (OpenAI & Google Gemini)  
- **[✅] Milestone 2.7**: Web Application Phase 1 - Backend API with FastAPI
- **[✅] Milestone 3.1**: ProjectScanningAgent with hierarchical analysis
- **[✅] Milestone 3.2**: Risk Prediction Model with code metrics
- **[✅] Milestone 3.3**: Sequence Diagram Generation for Python & Java
- **[✅] Milestone 3.4**: Kotlin & Android Support with specialized static analysis
- **[✅] Milestone 3.5**: Web Application Phase 2 - Interactive Features

### **🎯 Current Status: Production-Ready Web Application**

The system now features a **complete interactive web application** with:

#### **Backend Capabilities**
- **Async Scan Processing**: Real-time progress tracking with task queue management
- **RESTful API**: Complete FastAPI backend with comprehensive endpoints
- **Multi-Language Support**: Python, Java, Kotlin analysis with 50+ static analysis rules
- **Advanced Features**: Risk prediction, sequence diagrams, project scanning
- **Production-Ready**: Comprehensive error handling, logging, and validation

#### **Frontend Capabilities**
- **Interactive Diagram Viewer**: Zoom, pan, export functionality for class and sequence diagrams
- **Language-Specific Viewers**: 
  - **Java Report Viewer**: Package hierarchy, class explorer, metrics visualization
  - **Kotlin Report Viewer**: Extension functions, coroutines, data classes, companion objects
  - **Sequence Diagram Viewer**: Timeline navigation, actor highlighting, interaction analysis
- **Responsive Design**: Mobile-friendly interface with accessibility compliance
- **Real-time Updates**: Progress tracking for scan processing with WebSocket-style updates

#### **Available Features**
- **Scan Management**: Create, monitor, and manage code analysis scans
- **Interactive Reports**: Comprehensive analysis results with filtering and sorting
- **Diagram Export**: High-quality SVG/PNG export for documentation
- **Error Handling**: Graceful degradation with user-friendly error messages
- **Performance Optimization**: Lazy loading for large datasets and reports

## **Usage Guide**

### **Web Application Usage**

1. **Start the Application:**
   ```bash
   # Start both backend and frontend
   python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000
   cd src/webapp/frontend && npm run dev
   ```

2. **Access the Interface:**
   - Open browser to http://localhost:5173
   - Navigate through the intuitive web interface

3. **Create a Scan:**
   - Click "New Scan" button
   - Enter repository URL and configuration
   - Select scan type (PR or Full Project)
   - Monitor real-time progress

4. **View Results:**
   - Browse scan results in the dashboard
   - Use language-specific viewers for detailed analysis
   - Interact with diagrams (zoom, pan, export)
   - Filter and sort findings by severity or category
   - **Monitor Agent Workflow**: View real-time agent execution at `/workflow` or `/workflow-demo` for interactive visualization

### **API Usage**

```bash
# Get scan report
curl http://localhost:8000/scans/demo_scan_1/report

# Create new scan
curl -X POST http://localhost:8000/scans/initiate \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo", "scan_type": "pr", "pr_id": 123}'

# Monitor scan progress
curl http://localhost:8000/scans/jobs/{job_id}/status

# List all scans
curl http://localhost:8000/scans/
```

### **Command Line Testing**

```bash
# Test full setup (backend + frontend)
python scripts/test_full_setup.py

# Debug frontend issues (includes browser debugging)
python scripts/debug_frontend.py

# Test backend API only
python scripts/test_api_simple.py

# Run specific analysis demo
python scripts/demo_project_scanning.py
```

### **Verify Installation**

Sau khi cài đặt, sử dụng script test để kiểm tra:

```bash
# Test toàn bộ setup
python scripts/test_full_setup.py
```

Script này sẽ kiểm tra:
- ✅ Backend health và API endpoints
- ✅ Frontend development server
- ✅ API documentation (Swagger UI và ReDoc)
- ✅ Connectivity giữa các components

## **Architecture**

The system follows a modern, scalable architecture:

- **Frontend Layer**: React SPA with TypeScript, component-based architecture
- **API Layer**: FastAPI with async support, automatic OpenAPI documentation
- **Orchestration Layer**: Multi-Agent System using LangGraph for workflow management
- **Analysis Engine**: AST-based static analysis + Impact analysis (diff/dependency propagation) + LLM semantic analysis + Risk prediction
- **Diagramming Engine**: PlantUML/Mermaid generation with interactive frontend rendering
- **Data Layer**: JSON-based reports with future database integration support

### **Orchestrator Workflow (LangGraph)**

1. **start_scan**: Validate scan request, khởi tạo workflow
2. **fetch_code_node**: Lấy mã nguồn hoặc diff từ repo/PR
3. **parse_code_node**: Phân tích mã thành AST (Tree-sitter)
4. **static_analysis_node**: Phân tích tĩnh theo rule (StaticAnalysisAgent)
5. **impact_analysis_node**: Phân tích tác động thay đổi (ImpactAnalysisAgent) – xác định các thực thể bị ảnh hưởng trực tiếp/gián tiếp qua diff và dependency graph
6. **llm_analysis_node**: Phân tích ngữ nghĩa sâu bằng LLM (LLMOrchestratorAgent)
7. **project_scanning_node**: Tổng hợp kiến trúc, rủi ro toàn dự án (ProjectScanningAgent)
8. **reporting_node**: Tổng hợp kết quả, sinh báo cáo (ReportingAgent)
9. **handle_error_node**: Xử lý lỗi và sinh báo cáo lỗi

**ImpactAnalysisAgent** giúp đánh giá nhanh phạm vi ảnh hưởng của thay đổi, hỗ trợ reviewer tập trung vào các khu vực rủi ro cao, và cung cấp dữ liệu lan truyền tác động cho các bước phân tích tiếp theo.

## **Testing**

The project includes comprehensive testing at all levels:

### **Backend Testing**

```bash
# Run all backend tests
python -m pytest

# Run with coverage report
python -m pytest --cov=src

# Test specific components
python -m pytest tests/core_engine/agents/ -v
python -m pytest tests/webapp/backend/ -v
```

### **Frontend Testing**

```bash
# Navigate to frontend directory
cd src/webapp/frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run tests in UI mode
npm run test:ui
```

### **End-to-End Testing**

```bash
# Run E2E tests
cd src/webapp/frontend
npm run test:e2e

# Run with UI for debugging
npm run test:e2e:ui

# Debug specific tests
npm run test:e2e:debug
```

### **Test Coverage Summary**
- **Backend Components**: 95%+ coverage with 200+ test cases
- **Frontend Components**: Comprehensive component testing with MSW API mocking
- **Integration Tests**: Complete workflow testing from scan creation to report viewing
- **E2E Tests**: Full user journey testing with accessibility and performance validation

## **Demo and Examples**

### **Live Demo Features**

The web application includes built-in demo data showcasing:

- **Multi-language Analysis**: Python, Java, Kotlin sample reports
- **Interactive Diagrams**: Class diagrams and sequence diagrams with zoom/pan
- **Real-time Processing**: Simulated scan progress with task management
- **Agent Workflow Visualization**: Interactive multi-agent workflow at `/workflow-demo` with real-time status updates, node interactions, and detailed agent insights
- **Language-specific Features**: 
  - Java package hierarchy and method signature analysis
  - Kotlin extension functions and coroutine detection
  - Sequence diagram timeline navigation

### **Sample Reports**

Visit the running application to explore:
- `demo_scan_1`: Python project with security vulnerabilities
- `pr_scan_java_123`: Java PR analysis with performance issues  
- `project_scan_kotlin_456`: Kotlin Android project with architecture insights

## **Contributing**

### **Development Workflow**

1. **Check Current Tasks**: See `docs/TASK.md` for current development priorities
2. **Follow Standards**: 
   - Python: PEP8, type hints, Google-style docstrings
   - TypeScript: Strict mode, consistent component patterns
   - Testing: Comprehensive unit tests for all new features

3. **Testing Requirements**:
   - All new backend features must include unit tests
   - Frontend components require component tests
   - Complex features need integration tests

### **Code Quality Standards**

- **Backend**: 90%+ test coverage, comprehensive error handling
- **Frontend**: TypeScript strict mode, accessibility compliance
- **Documentation**: Update README.md and PLANNING.md for significant changes

## **Future Roadmap**

### **Milestone 4: Advanced Features (In Progress)**
- [ ] User authentication and project management
- [ ] Historical trend analysis and dashboard
- [ ] Advanced XAI visualization for LLM insights
- [ ] Performance optimization for large codebases
- [ ] Multi-user collaboration features

### **Phase 4: Enterprise Features**
- [ ] CI/CD integration capabilities
- [ ] Advanced security scanning
- [ ] Custom rule configuration
- [ ] API rate limiting and scaling
- [ ] Enterprise dashboard and reporting

## **License**

This project is based on the research and design outlined in "Report: AI-Based In-Depth Code Review System – Design and Roadmap (May 2025)".

---

## **Troubleshooting**

### **Common Issues and Solutions**

#### **Backend Import Error**
```bash
ERROR: Error loading ASGI app. Could not import module "src.webapp.backend.api.main".
```
**Solution**: Đảm bảo rằng bạn đang chạy lệnh từ thư mục gốc của dự án:
```bash
cd /path/to/aicode-reviewer
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000
```

#### **Module Not Found Error**
```bash
ModuleNotFoundError: No module named 'src'
```
**Solution**: Thêm thư mục hiện tại vào PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000
```

#### **Port Already in Use Error**
```bash
OSError: [Errno 48] Address already in use
```
**Solution**: Sử dụng port khác hoặc kill process đang sử dụng port 8000:
```bash
lsof -ti:8000 | xargs kill -9
# hoặc sử dụng port khác
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8001
```

#### **Frontend npm Install Issues**
```bash
npm ERR! code ERESOLVE
```
**Solution**: Clear npm cache và install lại:
```bash
cd src/webapp/frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### **API Requests Failing**
```bash
curl: (7) Failed to connect to localhost port 8000
```
**Solution**: Kiểm tra backend server đang chạy và accessible:
```bash
# Kiểm tra server đang chạy
curl http://localhost:8000/health

# Nếu không hoạt động, restart backend
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000
```

## **Quick Reference**

### **Key URLs**
- **Web App**: http://localhost:5173 (Frontend)
- **API**: http://localhost:8000 (Backend)
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **API Redoc**: http://localhost:8000/redoc (ReDoc UI)

### **Key Commands**
```bash
# Start development environment
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000
cd src/webapp/frontend && npm run dev

# Run all tests
python -m pytest && cd src/webapp/frontend && npm test

# Build for production
cd src/webapp/frontend && npm run build

# Test backend API directly
curl http://localhost:8000/health
curl http://localhost:8000/scans/demo_scan_1/report
```

### **Project Status**
- **Core Engine**: ✅ Complete with multi-language support
- **Backend API**: ✅ Production-ready with async processing
- **Frontend UI**: ✅ Interactive with specialized viewers
- **Testing**: ✅ Comprehensive coverage (unit, integration, E2E)
- **Documentation**: ✅ Complete setup and usage guides