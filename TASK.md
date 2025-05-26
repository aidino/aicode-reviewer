# **TASK.MD**

## **Current Sprint / Active Tasks (Derived from Phase 1\)**

* **\[TODO\]** Setup LangGraph Framework:  
  * **\[TODO\]** Basic agent communication structure.  
* **\[TODO\]** Develop CodeFetcherAgent for Python:  
  * **\[TODO\]** Implement PR diff retrieval for Python projects.  
  * **\[TODO\]** Implement full project code retrieval for Python projects.  
* **\[TODO\]** Develop ASTParsingAgent for Python:  
  * **\[TODO\]** Integrate Tree-sitter with Python grammar.  
  * **\[TODO\]** Implement AST generation for Python files.  
* **\[TODO\]** Develop basic StaticAnalysisAgent for Python:  
  * **\[TODO\]** Implement rule engine for Tree-sitter queries.  
  * **\[TODO\]** Define and implement 3-5 basic static analysis rules for Python (e.g., unused imports, simple style checks).  
* **\[TODO\]** Integrate one Open Source LLM:  
  * **\[TODO\]** Setup local hosting or API access for a chosen model (e.g., a smaller CodeLlama variant for initial testing).  
  * **\[TODO\]** Develop basic LLMOrchestratorAgent for simple prompt/response with the chosen LLM.  
* **\[TODO\]** Develop basic ReportingAgent:  
  * **\[TODO\]** Implement Markdown report generation (initial data structure for reports).  
  * **\[TODO\]** Aggregate findings from StaticAnalysisAgent and basic LLM insights.  
* **\[TODO\]** End-to-End Test for Python PR Scan (Basic \- CLI focused):  
  * **\[TODO\]** Test workflow: User request \-\> Code Fetch \-\> AST Parse \-\> Static Analysis \-\> Basic LLM analysis \-\> Report (data structure).

## **Milestones & Backlog (Derived from Roadmap)**

### **Milestone 1: Proof-of-Concept Core Engine & Single Language (End of Phase 1\)**

* **\[DONE/TODO\]** All "Current Sprint / Active Tasks" completed.  
* *Deliverable:* Basic Python PR scanning capability with diff summary, simple bug detection, and structured report data (initially for Markdown, adaptable for Web App).

### **Milestone 2: Enhanced Analysis, Diagramming & Basic Web App (End of Phase 2\)**

* **\[BACKLOG\]** Expand StaticAnalysisAgent rule set for Python.  
* **\[BACKLOG\]** Develop RAGContextAgent for Python:  
  * **\[BACKLOG\]** Implement code chunking (AST-aware).  
  * **\[BACKLOG\]** Setup vector database and embedding generation for Python code.  
  * **\[BACKLOG\]** Implement RAG retrieval for Python context.  
* **\[BACKLOG\]** Develop SolutionSuggestionAgent for Python:  
  * **\[BACKLOG\]** Integrate with LLMOrchestratorAgent to refine LLM outputs into actionable solutions.  
* **\[BACKLOG\]** Develop DiagramGenerationAgent for Python Class Diagrams:  
  * **\[BACKLOG\]** Extract class structure from Python ASTs.  
  * **\[BACKLOG\]** Generate PlantUML/Mermaid syntax for Python class diagrams.  
  * **\[BACKLOG\]** Highlight changes on diagrams for PRs.  
* **\[BACKLOG\]** Basic Java Support (Core Analysis):  
  * **\[BACKLOG\]** Implement CodeFetcherAgent and ASTParsingAgent for Java.  
  * **\[BACKLOG\]** Basic StaticAnalysisAgent rules for Java.  
* **\[BACKLOG\]** Integrate Pluggable Commercial LLM APIs (OpenAI/Gemini).  
* **\[BACKLOG\]** **Web Application \- Phase 1 (Basic Report Viewing):**  
  * **\[BACKLOG\]** Design basic Backend API (e.g., FastAPI) for report data.  
  * **\[BACKLOG\]** Develop ReportingAgent to output structured JSON for the Web App.  
  * **\[BACKLOG\]** Frontend: Setup project (e.g., React/Vue).  
  * **\[BACKLOG\]** Frontend: Implement UI for listing scans/reports.  
  * **\[BACKLOG\]** Frontend: Implement UI for displaying basic report details (findings, suggestions from ReportingAgent).  
  * **\[BACKLOG\]** Frontend: Basic rendering of PlantUML/Mermaid class diagrams (Python).  
* *Deliverable:* Actionable solution suggestions for Python. Basic class diagrams for Python PRs. **Basic Web App for viewing Python scan reports and class diagrams.** Basic Java analysis capabilities.

### **Milestone 3: Full Project Scanning, Advanced Features & Enhanced Web App (End of Phase 3\)**

* **\[BACKLOG\]** Develop ProjectScanningAgent for Python & Java.  
* **\[BACKLOG\]** Initial Risk Prediction Model.  
* **\[BACKLOG\]** DiagramGenerationAgent for Sequence Diagrams (Python & Java).  
* **\[BACKLOG\]** Basic Kotlin & Android Support (Core Analysis).  
* **\[BACKLOG\]** **Web Application \- Phase 2 (Interactive Features & Broader Support):**  
  * **\[BACKLOG\]** Backend API: Endpoints for initiating scans, managing projects.  
  * **\[BACKLOG\]** Frontend: UI for initiating PR and project scans.  
  * **\[BACKLOG\]** Frontend: Enhanced report visualization (e.g., filtering, sorting issues).  
  * **\[BACKLOG\]** Frontend: Interactive diagram features (e.g., zoom, pan, click-to-code if feasible).  
  * **\[BACKLOG\]** Frontend: Display sequence diagrams.  
  * **\[BACKLOG\]** Frontend: Support for Java reports and diagrams.  
  * **\[BACKLOG\]** Frontend: User authentication/management (if required for self-hosting multi-user scenarios).  
* *Deliverable:* Full project scanning capability. Architectural insights. Initial Kotlin/Android support. **Enhanced Web App with scan initiation, interactive diagrams, and Java support.**

### **Milestone 4: Multi-language Expansion, Optimization & Mature Web App (Ongoing \- Phase 4\)**

* **\[BACKLOG\]** Expand support to other languages based on priority.  
* **\[BACKLOG\]** Performance optimization (AST parsing, LLM inference, RAG retrieval, Web App responsiveness).  
* **\[BACKLOG\]** Implement user feedback mechanisms (for RLHF/prompt refinement) **via Web App**.  
* **\[BACKLOG\]** Regular updates to LLMs, Tree-sitter grammars.  
* **\[BACKLOG\]** Advanced Explainable AI (XAI) techniques for LLM suggestions, **visualized in Web App**.  
* **\[BACKLOG\]** **Web Application \- Phase 3 (Advanced Features & Polish):**  
  * **\[BACKLOG\]** Dashboard for project health overview.  
  * **\[BACKLOG\]** Historical trend analysis of code quality/risks.  
  * **\[BACKLOG\]** Customizable report views.  
  * **\[BACKLOG\]** Support for Kotlin/Android reports and diagrams in Web App.  
* *Deliverable:* Mature, multi-language system with continuous improvement. **Full-featured Web App for comprehensive code review management and visualization.**

## **Discovered Mid-Process / New Tasks**

* *(Empty \- to be filled as project progresses)*