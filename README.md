# **AI-Powered In-Depth Code Review System**

## **Project Overview**

This project aims to develop a sophisticated, AI-driven system for in-depth code review. Leveraging Large Language Models (LLMs) and Abstract Syntax Tree (AST) analysis, the system is designed to provide deep semantic understanding of code changes, identify potential issues, and offer actionable solutions. It supports on-demand scanning for both individual Pull Requests (PRs) and entire projects.

The core mission is to significantly improve code quality, enhance developer productivity, and maintain the integrity of software architecture. By offering comprehensive, automated analysis, the system helps in proactively identifying risks, reducing technical debt, and accelerating development cycles.

## **Key Features**

* **Deep Semantic Analysis:** Utilizes LLMs for a nuanced understanding of code logic, intent, and potential bugs beyond simple static checks.  
* **Hybrid Analysis Model:** Combines the structural precision of AST-based analysis with the contextual understanding of LLMs and Retrieval Augmented Generation (RAG).  
* **Multi-Agent Architecture:** Employs a system of specialized AI agents (orchestrated by LangGraph) to handle distinct tasks in the review process, such as code fetching, parsing, static analysis, LLM interaction, and report generation.  
* **Interactive Web Application:** Modern React-based frontend with interactive diagram visualization, zoom/pan capabilities, and specialized language viewers.
* **Actionable Error Resolution:** Focuses on generating clear, context-aware, and practical suggestions to help developers easily fix identified issues.  
* **Advanced Diagram Generation:** Generates interactive class diagrams and sequence diagrams (using PlantUML/Mermaid.js) with timeline navigation and export capabilities.
* **Multi-Language Support:** Python, Java, Kotlin (including Android-specific analysis) with language-specific report viewers.
* **Real-time Scan Processing:** Async scan initiation with progress tracking and task management.
* **On-Demand Scanning:** Allows users (developers, tech leads) to initiate scans for specific PRs (open or closed) or entire projects as needed.  
* **Comprehensive Reporting:** Produces detailed reports with interactive visualization, filtering, and export capabilities.
* **Standalone & Self-Hosted:** Designed to operate as an independent tool, self-hosted by the user to ensure data privacy and control over proprietary code.  
* **Open Source Prioritization:** Built with a strong preference for open-source technologies and components.

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
│   │   │   ├── models/           # Pydantic data models
│   │   │   └── services/         # Business logic services
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

### **Quick Start**

1. **Clone the repository:**
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
- **Tree-sitter**: AST parsing for multiple programming languages (Python, Java, Kotlin)
- **GitPython**: Git repository interaction
- **Radon**: Code complexity metrics calculation
- **pytest**: Testing framework with async support

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
# Test backend API
python scripts/test_api_simple.py

# Run specific analysis demo
python scripts/demo_project_scanning.py
```

## **Architecture**

The system follows a modern, scalable architecture:

- **Frontend Layer**: React SPA with TypeScript, component-based architecture
- **API Layer**: FastAPI with async support, automatic OpenAPI documentation
- **Orchestration Layer**: Multi-Agent System using LangGraph for workflow management
- **Analysis Engine**: AST-based static analysis + LLM semantic analysis + Risk prediction
- **Diagramming Engine**: PlantUML/Mermaid generation with interactive frontend rendering
- **Data Layer**: JSON-based reports with future database integration support

For detailed architecture information, see `docs/PLANNING.md`.

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
```

### **Project Status**
- **Core Engine**: ✅ Complete with multi-language support
- **Backend API**: ✅ Production-ready with async processing
- **Frontend UI**: ✅ Interactive with specialized viewers
- **Testing**: ✅ Comprehensive coverage (unit, integration, E2E)
- **Documentation**: ✅ Complete setup and usage guides