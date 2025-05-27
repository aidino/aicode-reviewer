# TASK_v2.md - Task List for Completing the AI Code Reviewer System

## 1. Completed Tasks
- [x] Built Orchestrator (LangGraph), defined workflow, state, >80% test coverage
- [x] Implemented main agents: CodeFetcher, ASTParsing, StaticAnalysis, LLMOrchestrator, RAGContext, Diagramming, Reporting, ProjectScanning, KnowledgeGraph, RiskPredictor
- [x] Integrated backend API (FastAPI): initiate scan, status, report, list, delete
- [x] Built frontend: scan creation, scan list, report viewing, diagram display
- [x] Unit tests for agents, API, frontend (Pytest, Jest)
- [x] Documentation: architecture, setup guide, usage examples
- [x] Separated ImpactAnalysisAgent: tạo module, models, unit test khung (2024-06-10)

## 2. Remaining/Additional Tasks
### 2.1. Core Engine & Agents
- [x] **Separate ImpactAnalysisAgent**
  - [x] Design interface và models cho change impact analysis (diff, dependency, propagation)
  - [x] Cài đặt logic analyze_impact (diff, dependency, propagation)
  - [x] Tích hợp vào orchestrator và reporting
  - [x] Viết unit tests cho agent (khung, models)
- [x] **Upgrade SolutionSuggestionAgent** (2024-12-19)
  - [x] Add explainable capability (reasoning, confidence, evidence)
  - [x] Diversify suggestions (multiple options, pros/cons analysis)
  - [x] Test edge cases, LLM errors

### 2.2. UI/UX & Visualization (Update May 2025)
- [x] **Modernize UI/UX (2025 trend)** (2024-12-19)
  - [x] Redesign layout for minimalism, clarity, and responsiveness
  - [x] Implement neumorphism/glassmorphism/soft shadow effects
  - [x] Update color palette (deep blue, electric blue, emerald green, orange, light/dark mode)
  - [x] Add smooth transitions, micro-interactions, and animated feedback
  - [x] Ensure accessibility (WCAG 2.2), high contrast, keyboard navigation
  - [x] Add customizable theme (light/dark, accent color switch)
  - [x] Use modern font and icon set
- [ ] **Agent Graph Visualization**
  - [ ] Visualize agent workflow as interactive graph (D3.js, Cytoscape.js, or React Flow)
  - [ ] Show agent status (idle, running, completed, error) with color coding
  - [ ] Highlight currently active agent(s) in real-time during scan
  - [ ] Allow click on agent node to view logs, input/output, or explanation
  - [ ] Animate transitions as workflow progresses
  - [ ] Sync with backend orchestrator state (WebSocket or polling)
  - [ ] Embed agent graph in scan progress/report page
  - [ ] Optionally allow replay of agent workflow for completed scans

### 2.3. Testing & Reliability
- [ ] Add tests for edge cases:
  - [ ] Network errors when fetching repo/PR
  - [ ] LLM timeout, invalid responses
  - [ ] Vector store/Neo4j down or disconnected
  - [ ] Large files, codebase exceeding thresholds
- [ ] Test recovery capability, clear error reporting to users

### 2.4. Documentation & Guides
- [ ] Write guide for extending static analysis rules (add new rule, DSL rule)
- [ ] Guide for adding new languages (Tree-sitter grammar, agent mapping)
- [ ] Guide for custom prompts, integrating new LLMs
- [ ] Guide for extending diagrams (class, sequence, C4 architecture)

### 2.5. CI/CD & DevOps
- [ ] Build CI/CD pipeline for automated testing, build, deploy
- [ ] Integrate coverage, lint, frontend/backend test checks

### 2.6. UI/UX & Administration
- [ ] (Optional) Build static rule management UI
- [ ] (Optional) Add user permission, LLM API key management

## 3. Discovered During Work
- [ ] Optimize performance for large codebases, reduce LLM cost
- [ ] Add warnings when scan exceeds resource thresholds
- [ ] Optimize knowledge base storage, periodic vector store cleanup

---
*This file was auto-generated based on codebase and research document review on 2024-06-09. Last updated with UI/UX and agent graph features (May 2025).* 