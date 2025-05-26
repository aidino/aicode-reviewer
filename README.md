# **AI-Powered In-Depth Code Review System**

## **Project Overview**

This project aims to develop a sophisticated, AI-driven system for in-depth code review. Leveraging Large Language Models (LLMs) and Abstract Syntax Tree (AST) analysis, the system is designed to provide deep semantic understanding of code changes, identify potential issues, and offer actionable solutions. It supports on-demand scanning for both individual Pull Requests (PRs) and entire projects.

The core mission is to significantly improve code quality, enhance developer productivity, and maintain the integrity of software architecture. By offering comprehensive, automated analysis, the system helps in proactively identifying risks, reducing technical debt, and accelerating development cycles.

## **Key Features**

* **Deep Semantic Analysis:** Utilizes LLMs for a nuanced understanding of code logic, intent, and potential bugs beyond simple static checks.  
* **Hybrid Analysis Model:** Combines the structural precision of AST-based analysis with the contextual understanding of LLMs and Retrieval Augmented Generation (RAG).  
* **Multi-Agent Architecture:** Employs a system of specialized AI agents (orchestrated by LangGraph) to handle distinct tasks in the review process, such as code fetching, parsing, static analysis, LLM interaction, and report generation.  
* **Actionable Error Resolution:** Focuses on generating clear, context-aware, and practical suggestions to help developers easily fix identified issues.  
* **Automated Architectural Diagramming:** Generates class diagrams and sequence diagrams (using PlantUML/Mermaid.js) to visualize code structure, changes within a PR, and their potential impact on the existing architecture.  
* **On-Demand Scanning:** Allows users (developers, tech leads) to initiate scans for specific PRs (open or closed) or entire projects as needed.  
* **Comprehensive Reporting:** Produces detailed reports in human-readable formats (Markdown, HTML) and potentially machine-readable formats (SARIF), summarizing findings, proposed solutions, and architectural visualizations.  
* **Standalone & Self-Hosted:** Designed to operate as an independent tool, self-hosted by the user to ensure data privacy and control over proprietary code. It does not directly integrate into CI/CD pipelines, acting as an offline analysis and reporting tool.  
* **Open Source Prioritization:** Built with a strong preference for open-source technologies and components.  
* **Initial Language Support:** Python, Java, Kotlin (including Android-specific analysis).

## **Strategic Value**

This system moves beyond traditional linters and basic static analysis tools by:

* Providing proactive and in-depth code quality assurance.  
* Offering insights into architectural health and potential risks.  
* Reducing the manual effort in code reviews, allowing senior developers to focus on more complex design challenges.  
* Facilitating a culture of high-quality engineering and continuous improvement.

## **Project Structure**

```
aicode-reviewer/
├── src/                           # Main source code
│   ├── core_engine/              # Core analysis engine
│   │   ├── agents/               # LangGraph agents (CodeFetcher, ASTParser, etc.)
│   │   ├── orchestrator.py       # Main workflow orchestration
│   │   └── diagramming_engine.py # Diagram generation logic
│   ├── webapp/                   # Web application
│   │   └── backend/              # FastAPI backend
│   │       ├── api/              # API routes and endpoints
│   │       ├── models/           # Pydantic data models
│   │       └── services/         # Business logic services
│   ├── reporting/                # Report generation and formatting
│   ├── utils/                    # Utility functions and helpers
│   └── main.py                   # Application entry point
├── tests/                        # Unit tests mirroring src structure
│   ├── core_engine/              # Core engine tests
│   └── webapp/backend/           # Webapp backend tests
├── scripts/                      # Demo and utility scripts
│   ├── demo_webapp_backend.py    # Webapp backend demo
│   └── test_api_simple.py        # Simple API testing
├── docs/                         # Documentation (PLANNING.md, TASK.md)
├── config/                       # Configuration files and settings
├── requirements.txt              # Python dependencies
└── .env.example                 # Environment variables template
```

## **Setup and Installation**

### **Prerequisites**

- Python 3.8 or higher
- Git
- Optional: CUDA-compatible GPU for local LLM inference

### **Installation Steps**

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd aicode-reviewer
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

### **Dependencies**

The project uses the following key dependencies:

- **LangChain & LangGraph**: Multi-agent orchestration framework
- **FastAPI**: Web API framework for the backend
- **Tree-sitter**: AST parsing for multiple programming languages
- **GitPython**: Git repository interaction
- **pytest**: Testing framework with async support
- **httpx**: HTTP client for API testing

## **Development Status**

This project is currently in **Phase 2 - Enhanced Analysis & Basic Web App** development. See `docs/TASK.md` for current sprint tasks and milestones.

### **Completed Milestones**

- [✅] **Milestone 1**: Proof-of-Concept Core Engine & Single Language  
- [✅] **Milestone 2.5**: Basic Java Support
- [✅] **Milestone 2.6**: Commercial LLM APIs Integration (OpenAI & Google Gemini)
- [✅] **Milestone 2.7**: Web Application Phase 1 - Backend API

### **Current Status: Web Application Backend Completed**

The backend API for the web application has been successfully implemented with:

- **RESTful API Endpoints**: Complete FastAPI backend with scan management
- **Comprehensive Data Models**: Pydantic models matching core engine output
- **Mock Data Service**: Realistic scan reports for development and testing  
- **Full Test Coverage**: 16 comprehensive unit tests with error handling
- **Production-Ready Code**: Proper validation, logging, and dependency injection

**Available Endpoints:**
- `GET /scans/{scan_id}/report` - Retrieve detailed scan reports
- `GET /scans/{scan_id}/status` - Check scan status
- `POST /scans/` - Create new scans
- `GET /scans/` - List scans with pagination
- `DELETE /scans/{scan_id}` - Delete scans

### **Next Steps: Frontend Development**

- [ ] Frontend: Setup project (React/Vue)
- [ ] Frontend: Implement UI for listing scans/reports  
- [ ] Frontend: Display basic report details and findings
- [ ] Frontend: Basic rendering of PlantUML/Mermaid diagrams

## **Architecture**

The system follows a modular, multi-agent architecture built on LangGraph. Key components include:

- **User Interface Layer**: Web Application (FastAPI) for scan management and report viewing
- **Orchestration Layer**: Multi-Agent System using LangGraph
- **Analysis Engine**: AST-based static analysis + LLM semantic analysis
- **Reporting Engine**: Structured report generation with diagram support
- **Knowledge Base**: Vector store for RAG context

For detailed architecture information, see `docs/PLANNING.md`.

## **Testing**

The project includes comprehensive unit tests for all components:

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src

# Run specific test module
python -m pytest tests/webapp/backend/api/test_scan_routes.py -v

# Run webapp backend API tests
python scripts/test_api_simple.py
```

**Test Coverage:**
- **Webapp Backend API**: 16 comprehensive test cases with error handling
- **Core Engine Components**: Individual agent tests with mock data
- **Integration Tests**: End-to-end workflow testing

## **Demo and Usage**

### **Testing the Webapp Backend API**

```bash
# Simple API test using TestClient
python scripts/test_api_simple.py

# Full demo with server (requires uvicorn)
python scripts/demo_webapp_backend.py
```

**Sample API Usage:**

```bash
# Get scan report
curl http://localhost:8000/scans/demo_scan_1/report

# Create new scan
curl -X POST http://localhost:8000/scans/ \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo", "scan_type": "pr", "pr_id": 123}'

# List all scans
curl http://localhost:8000/scans/
```

## **Contributing**

Please refer to `docs/TASK.md` for current development tasks and priorities. All contributions should follow the project's coding standards and include appropriate unit tests.

## **License**

This project is based on the research and design outlined in "Report: AI-Based In-Depth Code Review System – Design and Roadmap (May 2025)".