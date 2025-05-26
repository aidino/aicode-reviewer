# **Prompts for Cursor AI: AI Code Review Project Development (End-to-End with Testing)**

This document provides a comprehensive series of prompts for Cursor AI to guide the development of the AI Code Review project. These prompts cover project initialization, feature implementation, and robust testing (unit and integration tests) for each significant component, aligning with PLANNING.MD and TASK.MD.

## **General Instruction for Cursor (Remind Cursor at the start of each major phase):**

"Refer to the PLANNING.MD and TASK.MD documents for all architectural decisions, technology stack choices, component responsibilities, and task breakdowns when generating code, project structure, and test cases. Ensure all Python code includes type hints and comprehensive docstrings."

## **Phase 1: Proof-of-Concept Core Engine & Single Language (Python)**

### **Milestone 1.1: Project Setup and Core Directory Structure**

**(Same as your existing Prompt 1 \- this is foundational)**

Prompt to Cursor (Project Setup):  
"Initialize a new Python project for an AI Code Review system.  
Referencing PLANNING.MD (Sections: Overall Architecture, Technology Stack) and TASK.MD (Milestone 1 setup):

1. Create the root project directory named ai\_code\_reviewer.  
2. Inside ai\_code\_reviewer, create top-level directories: src, scripts, tests, docs, config.  
3. Initialize a Git repository.  
4. Create a Python-specific .gitignore.  
5. Create requirements.txt with: langchain, langgraph, python-dotenv, fastapi, uvicorn\[standard\], requests, GitPython, tree-sitter, pytest, pytest-cov, pytest-asyncio (for FastAPI async tests), httpx (for testing FastAPI).  
6. Create a placeholder README.md in root (from artifact).  
7. Copy PLANNING.MD and TASK.MD into docs/."

### **Milestone 1.2: LangGraph Orchestration Layer Setup**

**Task: Implement Basic LangGraph Orchestrator**

Prompt to Cursor (Implementation \- Orchestrator):  
"Referencing PLANNING.MD (Sections: Overall Architecture, Multi-Agent Framework) and TASK.MD (Phase 1):  
Inside src/core\_engine/, create orchestrator.py.

1. Define a Pydantic model for the graph's state (e.g., GraphState including fields like scan\_request\_data: dict, repo\_url: str, pr\_id: Optional\[int\], project\_code: Optional\[dict\[str, str\]\], pr\_diff: Optional\[str\], parsed\_asts: Optional\[dict\[str, Any\]\], static\_analysis\_findings: Optional\[list\[dict\]\], llm\_insights: Optional\[str\], report\_data: Optional\[dict\], error\_message: Optional\[str\]).  
2. Initialize a StatefulGraph with this GraphState.  
3. Define placeholder functions for initial nodes (e.g., start\_scan, fetch\_code\_node, parse\_code\_node, static\_analysis\_node, llm\_analysis\_node, reporting\_node, handle\_error\_node). These functions should take state: GraphState as input and return a partial GraphState update.  
4. Add these functions as nodes to the graph.  
5. Define conditional edges based on state (e.g., if pr\_id is present, go to PR fetching; otherwise, project fetching. If an error occurs, go to handle\_error\_node).  
6. Set entry and finish points.  
7. Create a function compile\_graph() that returns the compiled app \= graph.compile().  
8. Add comments indicating where agent logic will be integrated into each node function."

Prompt to Cursor (Unit Tests \- Orchestrator):  
"In tests/core\_engine/, create test\_orchestrator.py.  
Write unit tests for src/core\_engine/orchestrator.py:

1. Test that the GraphState model can be instantiated correctly.  
2. Test that compile\_graph() returns a runnable LangGraph application.  
3. (Optional, if simple logic is in nodes) Test individual placeholder node functions to ensure they correctly update the state with mock data (e.g., start\_scan populating scan\_request\_data)."

### **Milestone 1.3: CodeFetcherAgent Implementation & Testing**

**Task: Implement CodeFetcherAgent for Python**

Prompt to Cursor (Implementation \- CodeFetcherAgent):  
"Referencing PLANNING.MD (Agent Roles: CodeFetcherAgent) and TASK.MD (Phase 1):  
Create src/core\_engine/agents/code\_fetcher\_agent.py.  
Define the CodeFetcherAgent class.

1. Implement \_\_init\_\_(self).  
2. Implement get\_pr\_diff(self, repo\_url: str, pr\_id: int, target\_branch: str, source\_branch: str) \-\> str:  
   * Use GitPython to clone/fetch the repo.  
   * Checkout target\_branch and source\_branch.  
   * Compute the diff between them. Handle potential errors (e.g., invalid URL, branches not found).  
   * Consider using a temporary directory for cloning.  
3. Implement get\_project\_files(self, repo\_url: str, branch\_or\_commit: str) \-\> dict\[str, str\]:  
   * Use GitPython to clone/fetch the repo.  
   * Checkout the specified branch\_or\_commit.  
   * Iterate through project files (Python files initially), read their content, and return a dictionary mapping file paths to their content. Handle errors.  
     In src/core\_engine/orchestrator.py, update the fetch\_code\_node to instantiate and use CodeFetcherAgent."

Prompt to Cursor (Unit Tests \- CodeFetcherAgent):  
"In tests/core\_engine/agents/, create test\_code\_fetcher\_agent.py.  
Write unit tests for CodeFetcherAgent using pytest and unittest.mock:

1. Mock git.Repo.clone\_from and other relevant GitPython methods.  
2. Test get\_pr\_diff with valid inputs, ensuring it calls GitPython methods correctly and returns a mock diff. Test error handling for invalid repo URLs or PRs (e.g., by having mocks raise exceptions).  
3. Test get\_project\_files with valid inputs, ensuring it calls GitPython methods, iterates files, and returns mock file content. Test error handling."

### **Milestone 1.4: ASTParsingAgent Implementation & Testing**

**Task: Implement ASTParsingAgent for Python**

Prompt to Cursor (Implementation \- ASTParsingAgent):  
"Referencing PLANNING.MD (Agent Roles: ASTParsingAgent, Tech Stack: Tree-sitter) and TASK.MD (Phase 1):  
Create src/core\_engine/agents/ast\_parsing\_agent.py.  
Define the ASTParsingAgent class.

1. Implement \_\_init\_\_(self):  
   * Initialize Tree-sitter Parser.  
   * Load the Python language grammar (Language.build\_library and set parser language). Handle potential errors if grammar file is not found.  
2. Implement parse\_code\_to\_ast(self, code\_content: str, language: str) \-\> tree\_sitter.Node | None:  
   * Check if the requested language is supported (initially 'python').  
   * Use the configured Tree-sitter parser to parse code\_content.  
   * Return the root node of the AST. Return None or raise an exception if parsing fails critically.  
     In src/core\_engine/orchestrator.py, update the parse\_code\_node to instantiate and use ASTParsingAgent."

Prompt to Cursor (Unit Tests \- ASTParsingAgent):  
"In tests/core\_engine/agents/, create test\_ast\_parsing\_agent.py.  
Write unit tests for ASTParsingAgent:

1. Test \_\_init\_\_ for successful parser and language setup (mock Language.build\_library if needed to avoid filesystem dependency in test).  
2. Test parse\_code\_to\_ast with a simple, valid Python code snippet. Verify that a tree\_sitter.Node object is returned and its type is as expected (e.g., 'module').  
3. Test parse\_code\_to\_ast with Python code containing syntax errors. Verify behavior (e.g., returns a node with error markers, or None, or raises a specific exception, depending on desired error handling).  
4. Test parse\_code\_to\_ast with an unsupported language, ensuring it handles this gracefully."

### **Milestone 1.5: Basic StaticAnalysisAgent Implementation & Testing**

**Task: Implement basic StaticAnalysisAgent for Python (3-5 rules)**

Prompt to Cursor (Implementation \- StaticAnalysisAgent):  
"Referencing PLANNING.MD (Agent Roles: StaticAnalysisAgent, AST-based rules) and TASK.MD (Phase 1):  
Create src/core\_engine/agents/static\_analysis\_agent.py.  
Define the StaticAnalysisAgent class.

1. Implement \_\_init\_\_(self):  
   * Load Python language for Tree-sitter queries.  
2. Implement \_query\_ast(self, ast\_node: tree\_sitter.Node, query\_string: str) \-\> list\[tuple\[tree\_sitter.Node, dict\]\]:  
   * Helper to execute a Tree-sitter query and return captures.  
3. Implement \_check\_rule\_example\_unused\_import(self, ast\_node: tree\_sitter.Node) \-\> list\[dict\]:  
   * Define a Tree-sitter query to find unused imports (this is complex; a simpler rule might be better for PoC, e.g., presence of pdb.set\_trace()).  
   * For a simpler PoC rule: \_check\_rule\_pdb\_set\_trace(self, ast\_node: tree\_sitter.Node) \-\> list\[dict\]:  
     * Query: ((import\_from\_statement module\_name: (dotted\_name (identifier) @mod) name: (dotted\_name (identifier) @imp)) (\#eq? @mod "pdb") (\#eq? @imp "set\_trace")) or (call function: (attribute object: (identifier) @obj attribute: (identifier) @attr) arguments: (argument\_list)) (\#eq? @obj "pdb") (\#eq? @attr "set\_trace")  
     * If found, return a finding dictionary: {'rule\_id': 'PDB\_TRACE\_FOUND', 'message': 'pdb.set\_trace() found.', 'line': node.start\_point\[0\] \+ 1, 'severity': 'Warning'}.  
4. Implement 2-3 more simple Python rules (e.g., use of print statements, function too long \- based on line numbers, class too long).  
5. Implement analyze\_python\_ast(self, ast\_node: tree\_sitter.Node) \-\> list\[dict\]:  
   * Call all implemented Python rule-checking methods and aggregate their findings.  
     In src/core\_engine/orchestrator.py, update the static\_analysis\_node to use StaticAnalysisAgent."

Prompt to Cursor (Unit Tests \- StaticAnalysisAgent):  
"In tests/core\_engine/agents/, create test\_static\_analysis\_agent.py.  
Write unit tests for StaticAnalysisAgent:

1. For each implemented rule (e.g., \_check\_rule\_pdb\_set\_trace):  
   * Test with a Python code snippet that *should* trigger the rule. Parse it to AST and pass the AST to the rule method. Verify the correct finding(s) are returned.  
   * Test with a Python code snippet that *should NOT* trigger the rule. Verify no findings are returned.  
2. Test analyze\_python\_ast by providing an AST that triggers multiple rules and one that triggers none. Verify aggregated results."

### **Milestone 1.6: Basic LLMOrchestratorAgent Implementation & Testing**

**Task: Implement basic LLMOrchestratorAgent (mocked LLM)**

Prompt to Cursor (Implementation \- LLMOrchestratorAgent):  
"Referencing PLANNING.MD (Agent Roles: LLMOrchestratorAgent) and TASK.MD (Phase 1):  
Create src/core\_engine/agents/llm\_orchestrator\_agent.py.  
Define the LLMOrchestratorAgent class.

1. Implement \_\_init\_\_(self, llm\_provider: str \= 'mock', api\_key: str \= None, model\_name: str \= None):  
   * Store provider, key, model.  
   * If llm\_provider \== 'mock', set up a mock LLM behavior.  
2. Implement invoke\_llm(self, prompt: str, code\_snippet: str \= None, static\_findings: list \= None) \-\> str:  
   * If mock provider: return a predefined mock response based on the prompt or inputs (e.g., "Mock LLM insight: Consider refactoring this code.").  
   * (Later, this will handle actual LLM API calls using Langchain chains/LCEL).  
   * Construct a full prompt if code\_snippet and static\_findings are provided.  
     In src/core\_engine/orchestrator.py, update the llm\_analysis\_node to use LLMOrchestratorAgent."

Prompt to Cursor (Unit Tests \- LLMOrchestratorAgent):  
"In tests/core\_engine/agents/, create test\_llm\_orchestrator\_agent.py.  
Write unit tests for LLMOrchestratorAgent:

1. Test \_\_init\_\_ with the 'mock' provider.  
2. Test invoke\_llm with the 'mock' provider:  
   * Call with a simple prompt and verify the expected mock response.  
   * Call with a prompt, code snippet, and static findings, and verify that the mock response is returned (and potentially that the prompt was constructed as expected if you add logic for that)."

### **Milestone 1.7: Basic ReportingAgent Implementation & Testing**

**Task: Implement basic ReportingAgent (Markdown & JSON structure)**

Prompt to Cursor (Implementation \- ReportingAgent):  
"Referencing PLANNING.MD (Agent Roles: ReportingAgent) and TASK.MD (Phase 1):  
Create src/core\_engine/agents/reporting\_agent.py.  
Define the ReportingAgent class.

1. Implement generate\_report\_data(self, static\_findings: list\[dict\], llm\_insights: str, scan\_details: dict) \-\> dict:  
   * Takes static analysis findings, LLM insights, and scan details (e.g., repo URL, PR ID).  
   * Constructs a structured dictionary (JSON-like) for the report. Example structure:  
     {'scan\_info': scan\_details, 'summary': {'total\_findings': len(static\_findings)}, 'static\_analysis\_findings': static\_findings, 'llm\_review': {'insights': llm\_insights}, 'diagrams': \[\]}.  
2. Implement format\_markdown\_report(self, report\_data: dict) \-\> str:  
   * Takes the structured report data.  
   * Formats it into a human-readable Markdown string.  
     In src/core\_engine/orchestrator.py, update the reporting\_node to use ReportingAgent."

Prompt to Cursor (Unit Tests \- ReportingAgent):  
"In tests/core\_engine/agents/, create test\_reporting\_agent.py.  
Write unit tests for ReportingAgent:

1. Test generate\_report\_data:  
   * Provide sample static\_findings, llm\_insights, and scan\_details.  
   * Verify the structure and content of the returned dictionary are correct.  
2. Test format\_markdown\_report:  
   * Provide sample structured report data (output from generate\_report\_data).  
   * Verify the generated Markdown string contains the expected sections and formatting. Test with empty findings and with multiple findings."

### **Milestone 1.8: Phase 1 Integration Test**

**Task: Create an integration test for the Phase 1 Python PR scan workflow.**

Prompt to Cursor (Integration Test \- Phase 1 Workflow):  
"In tests/core\_engine/, create test\_phase1\_integration.py.  
Write an integration test for the basic Python PR scan workflow:

1. This test will invoke the compiled LangGraph application from orchestrator.py.  
2. **Mock External Dependencies:**  
   * Mock CodeFetcherAgent methods to return predefined PR diff content (a simple Python code diff) and project file content without actual Git operations.  
   * Mock LLMOrchestratorAgent.invoke\_llm to return a predefined string.  
   * ASTParsingAgent and StaticAnalysisAgent should use their real implementations with Tree-sitter for Python.  
3. **Test Setup:**  
   * Prepare a sample scan\_request\_data dictionary for a Python PR.  
   * Ensure necessary Tree-sitter Python grammar is accessible for the test environment.  
4. **Test Execution:**  
   * Invoke the LangGraph app with the sample scan\_request\_data.  
   * Retrieve the final state from the graph execution.  
5. **Assertions:**  
   * Verify that static\_analysis\_findings in the final state contains expected findings based on the mocked PR diff and implemented static rules.  
   * Verify that llm\_insights in the final state matches the mocked LLM response.  
   * Verify that report\_data in the final state is structured correctly and contains the aggregated information.  
   * Assert that no error\_message is present in the final state."

## **Phase 2: Enhanced Analysis, Diagramming & Basic Web App**

(Continue this pattern for each task in Phase 2, 3, and 4 from TASK.MD)

### **Example for a Phase 2 Task: RAGContextAgent**

**Task: Implement RAGContextAgent for Python**

Prompt to Cursor (Implementation \- RAGContextAgent):  
"Referencing PLANNING.MD (Agent Roles: RAGContextAgent) and TASK.MD (Phase 2):  
Create src/core\_engine/agents/rag\_context\_agent.py.  
Define the RAGContextAgent class.

1. Implement \_\_init\_\_(self, vector\_store\_client, embedding\_model\_name: str):  
   * Initialize the vector store client (e.g., Qdrant, Weaviate \- mockable for now).  
   * Initialize an embedding model (e.g., from Langchain, HuggingFace \- mockable).  
2. Implement \_chunk\_code(self, file\_path: str, code\_content: str) \-\> list\[dict\]:  
   * Implement basic code chunking (e.g., by class/function using Tree-sitter, or simpler fixed-size chunks for PoC). Each chunk should be a dict with content and metadata (like file\_path, start\_line).  
3. Implement build\_knowledge\_base(self, project\_files: dict\[str, str\]):  
   * Iterate through project\_files.  
   * For each Python file, chunk its content using \_chunk\_code.  
   * Generate embeddings for each chunk (mock this call initially).  
   * Add chunks and their embeddings to the vector store (mock this call).  
4. Implement query\_knowledge\_base(self, query\_text: str, top\_k: int \= 3\) \-\> list\[str\]:  
   * Generate embedding for query\_text (mocked).  
   * Query the vector store for similar chunks (mocked).  
   * Return the content of the top\_k retrieved chunks.  
     In src/core\_engine/orchestrator.py, consider adding a node or modifying llm\_analysis\_node to use RAGContextAgent to fetch context before calling the LLM."

Prompt to Cursor (Unit Tests \- RAGContextAgent):  
"In tests/core\_engine/agents/, create test\_rag\_context\_agent.py.  
Write unit tests for RAGContextAgent:

1. Mock the vector store client and embedding model.  
2. Test \_chunk\_code with sample Python code, verifying the number and content of chunks.  
3. Test build\_knowledge\_base:  
   * Provide mock project\_files.  
   * Ensure \_chunk\_code is called for each file.  
   * Ensure embedding generation and vector store add methods are called with expected arguments (using mock.assert\_called\_with).  
4. Test query\_knowledge\_base:  
   * Ensure embedding generation for the query and vector store search methods are called.  
   * Verify it returns the mock retrieved chunk content."

### **Example for a Phase 2 Task: Web App Backend API Endpoint**

**Task: Implement Backend API for listing reports**

Prompt to Cursor (Implementation \- FastAPI Report Listing Endpoint):  
"Referencing PLANNING.MD (Web Application Backend API) and TASK.MD (Phase 2 \- Web App):  
In src/webapp/backend/api/scan\_routes.py:

1. Add a new GET endpoint /scans to the APIRouter.  
2. This endpoint should call a method in ScanService (e.g., list\_all\_scans()).  
3. The service method should (for now) return a list of mock ReportDetail Pydantic models.  
   In src/webapp/backend/services/scan\_service.py:  
4. Add list\_all\_scans(self) \-\> list\[ReportDetail\]. For now, return a hardcoded list of 2-3 mock ReportDetail objects.  
   Ensure ReportDetail is defined in src/webapp/backend/models/scan\_models.py."

Prompt to Cursor (Unit Tests \- FastAPI Report Listing Endpoint):  
"In tests/webapp/backend/api/, create test\_scan\_routes.py.  
Write unit tests for the /scans GET endpoint using pytest and httpx.AsyncClient:

1. Mock the ScanService.list\_all\_scans method to return a predefined list of mock report data.  
2. Make an async GET request to /scans.  
3. Assert the HTTP status code is 200\.  
4. Assert the response JSON matches the structure and content of the mocked data."

Prompt to Cursor (Integration Tests \- FastAPI Report Listing):  
"In tests/webapp/backend/, create test\_scan\_api\_integration.py.  
Write an integration test for the /scans endpoint:

1. This test will use the real ScanService (which returns mock data for now) and the real router.  
2. Use TestClient from fastapi.testclient or httpx.AsyncClient to make a GET request to /scans.  
3. Assert the status code and that the response data matches the mock data defined in ScanService."

## **Subsequent Phases (3 & 4\) \- Guiding Principles for Prompts:**

For each feature or enhancement in Phases 3 and 4, follow this prompt structure:

1. **Feature Implementation Prompt:**  
   * "Implement feature XYZ in module\_name.py / agent\_name.py / component\_name.tsx."  
   * "Refer to PLANNING.MD (relevant sections) and TASK.MD (specific task from the milestone)."  
   * Detail the specific methods, classes, UI elements, or API endpoints to be created or modified.  
   * Specify expected inputs, outputs, and core logic.  
   * Mention integration points with other components.  
2. **Unit Test Prompt:**  
   * "Write unit tests in tests/path/to/test\_module\_name.py for the newly implemented feature XYZ."  
   * "Focus on testing individual functions/methods/components in isolation."  
   * "Mock external dependencies (other agents, services, LLMs, databases, APIs)."  
   * "Cover valid inputs, edge cases, and error handling."  
3. **Integration Test Prompt (where applicable):**  
   * "Write integration tests in tests/path/to/test\_integration\_xyz.py for feature XYZ."  
   * "Test the interaction between component A and component B related to feature XYZ."  
   * "For backend: Test API endpoints with their underlying services (mocking only deeper dependencies like databases or external LLMs if necessary)."  
   * "For frontend (E2E): Use Playwright or Cypress to test user flows involving the new UI feature, mocking backend API responses if the backend is not yet fully integrated or for stability."  
   * "Ensure data flows correctly between integrated components."

**Example for a Phase 3 Feature: ProjectScanningAgent**

Prompt to Cursor (Implementation \- ProjectScanningAgent):  
"Implement the ProjectScanningAgent in src/core\_engine/agents/project\_scanning\_agent.py as per PLANNING.MD and TASK.MD (Phase 3).  
Focus on:

1. Method scan\_entire\_project(self, project\_files: dict\[str, str\]) \-\> dict.  
2. Logic for hierarchical summarization (placeholder or simple version initially).  
3. Integration with RAGContextAgent for project-wide context.  
4. Interaction with LLMOrchestratorAgent for analysis of summaries and context.  
5. Aggregation of results into a project health report structure."

Prompt to Cursor (Unit Tests \- ProjectScanningAgent):  
"Write unit tests for ProjectScanningAgent in tests/core\_engine/agents/test\_project\_scanning\_agent.py. Mock RAGContextAgent and LLMOrchestratorAgent. Test summarization logic and report aggregation."  
Prompt to Cursor (Integration Test \- ProjectScanningAgent with Orchestrator):  
"Update the LangGraph orchestrator in src/core\_engine/orchestrator.py to include a path for full project scans using ProjectScanningAgent. Write an integration test in tests/core\_engine/test\_project\_scan\_integration.py that invokes this path, mocking CodeFetcherAgent to provide project files and LLMOrchestratorAgent for LLM calls, but using the real ProjectScanningAgent and RAGContextAgent (with mocked DB/embeddings)."  
This detailed, iterative approach with prompts for implementation followed immediately by prompts for testing will help ensure a more robust and maintainable codebase as you develop with Cursor AI.