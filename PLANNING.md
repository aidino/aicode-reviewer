# **PLANNING.MD**

## **1\. High-Level Vision**

The project aims to develop an advanced, AI-driven code review system to significantly enhance code quality, developer productivity, and software architecture integrity. The system will provide in-depth semantic analysis using Large Language Models (LLMs), employ a multi-agent architecture for specialized task handling, and offer on-demand scanning capabilities for both Pull Requests (PRs) and entire projects. Key deliverables include actionable error resolution suggestions and automated generation of architectural diagrams (class and sequence diagrams) to visualize changes and their impacts. A strategic approach emphasizes a hybrid model, combining Abstract Syntax Trees (ASTs) for structural analysis with LLMs for nuanced understanding, prioritizing open-source components. The system is envisioned as a standalone tool, providing comprehensive reports primarily through a **Web Application** (and optionally a CLI), empowering developers to proactively improve code quality.

## **2\. Architecture**

### **2.1. Overall Architecture**

The system will feature a modular, microservices-inspired or component-based architecture.

* **Key Components:**  
  * **User Interface/Interaction Layer:** A **Web Application** for scan initiation, management, report viewing, and interactive diagram exploration. A Command Line Interface (CLI) can serve as an alternative for script-based interactions.  
  * **Backend API Layer:** Provides services for the Web Application, handling user requests, authentication (if needed), and communication with the Orchestration Layer.  
  * **Orchestration Layer:** Multi-Agent System (MAS) based on LangGraph.  
  * **Code Analysis Engine:** Modules for AST-based static analysis and LLM/RAG-based deep analysis.  
  * **Diagramming Engine:** Generates visual representations of code structure and changes.  
  * **Reporting Engine:** Aggregates findings into comprehensive review reports, accessible via the Web Application.  
  * **Knowledge Base/Vector Store:** For RAG context (code embeddings, documentation, architectural patterns).  
  * **Configuration & Rule Store:** For custom static analysis rules and system configurations.  
* **Data Flow:** Information (PR info, source code, ASTs, LLM prompts/responses, diagram data, report data) will flow between these components, managed by the Orchestration Layer and exposed to the user via the Web Application through the Backend API.

### **2.2. Multi-Agent Framework (LangGraph)**

LangGraph is chosen for its ability to model complex, stateful, and potentially iterative workflows inherent in comprehensive code review.

* **Agent Roles (Illustrative):**  
  * **UserInteractionAgent:** Handles scan requests from users (via Web App/CLI).  
  * **CodeFetcherAgent:** Retrieves PR diffs or full project code from Git repositories.  
  * **ASTParsingAgent:** Parses source code into ASTs using Tree-sitter.  
  * **StaticAnalysisAgent:** Performs rule-based checks on ASTs.  
  * **LLMOrchestratorAgent:** Manages interactions with LLMs for deep semantic analysis.  
  * **RAGContextAgent:** Builds and queries the RAG knowledge base.  
  * **DiagramGenerationAgent:** Generates data for class and sequence diagrams (using PlantUML/Mermaid.js), making them available for web rendering.  
  * **ImpactAnalysisAgent:** Analyzes code changes to identify affected components.  
  * **SolutionSuggestionAgent:** Refines LLM outputs into actionable solutions.  
  * **ProjectScanningAgent:** Orchestrates full project scans for holistic health assessment.  
  * **ReportingAgent:** Compiles findings into structured reports, preparing data for display in the Web Application.

## **3\. Constraints**

* **Standalone System:** The system will operate independently, generating reports primarily viewed through its Web Application. It does not directly integrate into CI/CD pipelines.  
* **Self-Hosted:** The system is designed to be self-hosted by the user.  
* **Data Privacy:**  
  * Prioritize locally hosted open-source LLMs.  
  * If commercial LLM APIs are used, ensure user awareness.  
* **Resource Requirements (Self-Hosting):**  
  * Sufficient CPU, RAM for agents, AST parsing, Web App backend.  
  * GPU(s) for efficient local LLM inference.  
* **Open Source Prioritization:** Maximize the use of mature, permissively licensed open-source components.  
* **Initial Language Focus:** Python, Java, Kotlin (including Android-specific constructs).

## **4\. Technology Stack & Tools**

### **4.1. Core Framework**

* **Orchestration:** Langchain/LangGraph (Python)

### **4.2. LLM Choices**

* **Open Source (Priority):** Models like DeepSeek Coder V2, Llama 3.1/3.3, StarCoder2, Qwen2.5, Mistral-Large, Phi-4, Gemma-2.  
* **Commercial APIs (Optional/Pluggable):** OpenAI (GPT-4o/GPT-X), Google Gemini (1.5 Pro/Flash), Anthropic Claude (3.5 Sonnet).

### **4.3. AST Parsing**

* **Core Parser:** Tree-sitter.  
* **Grammars:** Python, Java, Kotlin, XML (for Android).

### **4.4. Diagram Generation**

* **Syntax/Tools:** PlantUML, Mermaid.js (text-based definitions for backend generation).  
* **Frontend Rendering:** Libraries to render PlantUML/Mermaid.js or convert to interactive SVGs/canvas elements in the Web App.

### **4.5. Version Control Interaction**

* **Python:** GitPython.

### **4.6. Data Storage**

* **Vector Database (RAG):** Weaviate, Qdrant, Milvus, PostgreSQL with pgvector.  
* **Relational Database (Metadata, Agent State, Checkpoints, Web App Data):** PostgreSQL, SQLite.  
* **LangGraph Checkpointing:** Postgres, SQLite, Redis.

### **4.7. Web Application (User Interaction & Reporting)**

* **Backend Framework:**  
  * Python: FastAPI, Flask (recommended to align with LangGraph).  
  * Others: Spring Boot (Java), NestJS/Express (Node.js), Gin (Go).  
* **Frontend Framework:**  
  * React, Vue, Angular, Svelte.  
  * *Diagram Rendering:* Libraries compatible with PlantUML/Mermaid.js (e.g., official renderers, or custom solutions like Cytoscape.js for more interactivity).  
  * *Diff Viewer:* react-diff-viewer, jsdiff.  
  * *Syntax Highlighting:* Prism.js, Highlight.js.  
  * *UI Component Libraries:* Material UI, Ant Design, Tailwind CSS.

### **4.8. Static Analysis Inspiration**

* *Patterns from:* SonarQube/SonarLint, PMD, Checkstyle, ESLint, Ktlint, Bandit.

## **5\. Key Principles**

* **AST \+ LLM/RAG Hybrid:** Combine structured AST analysis with deep semantic understanding.  
* **Modularity:** Enable independent development and scaling.  
* **Actionable Feedback:** Focus on clear, context-aware, implementable solutions presented effectively in the Web App.  
* **User-Initiated Analysis via Web App:** Empower developers with an accessible interface for on-demand reviews.