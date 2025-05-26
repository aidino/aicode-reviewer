# Core Engine - LangGraph Orchestrator

## Overview

The Core Engine module contains the LangGraph orchestrator that coordinates the entire AI Code Review workflow. It implements a multi-agent system using LangGraph to manage the flow between different analysis stages.

## Architecture

### GraphState Model

The `GraphState` TypedDict defines the shared state that flows through all workflow nodes:

```python
class GraphState(TypedDict):
    scan_request_data: dict           # Original scan request parameters
    repo_url: str                     # Git repository URL
    pr_id: Optional[int]              # Pull request ID (if PR scan)
    project_code: Optional[Dict[str, str]]  # Full project files
    pr_diff: Optional[str]            # PR diff content
    parsed_asts: Optional[Dict[str, Any]]   # Parsed ASTs
    static_analysis_findings: Optional[List[dict]]  # Static analysis results
    llm_insights: Optional[str]       # LLM analysis insights
    report_data: Optional[dict]       # Final report data
    error_message: Optional[str]      # Error information
    current_step: str                 # Current workflow step
    workflow_metadata: dict           # Additional metadata
```

### Workflow Nodes

The orchestrator defines the following workflow nodes:

1. **start_scan**: Entry point, validates scan request
2. **fetch_code_node**: Retrieves code from Git repository
3. **parse_code_node**: Parses code into ASTs using Tree-sitter
4. **static_analysis_node**: Performs rule-based static analysis
5. **llm_analysis_node**: Conducts LLM-based semantic analysis
6. **reporting_node**: Generates final code review report
7. **handle_error_node**: Handles errors and generates error reports

### Conditional Flow

The workflow uses conditional edges to handle different scenarios:

- **PR vs Project Scan**: Automatically detects scan type and routes accordingly
- **Error Handling**: Any node can trigger error handling if issues occur
- **Step Progression**: Each step validates prerequisites before proceeding

## Usage

### Basic Usage

```python
from src.core_engine.orchestrator import compile_graph, GraphState

# Compile the workflow graph
app = compile_graph()

# Create initial state
initial_state = GraphState(
    scan_request_data={
        "repo_url": "https://github.com/example/repo",
        "pr_id": 123  # Optional: omit for full project scan
    },
    repo_url="",
    pr_id=None,
    project_code=None,
    pr_diff=None,
    parsed_asts=None,
    static_analysis_findings=None,
    llm_insights=None,
    report_data=None,
    error_message=None,
    current_step="start",
    workflow_metadata={}
)

# Execute the workflow
result = app.invoke(initial_state)
print("Final report:", result["report_data"])
```

### Integration with Agents

Each node function contains TODO comments indicating where specific agents should be integrated:

```python
def fetch_code_node(state: GraphState) -> Dict[str, Any]:
    # TODO: Integrate with CodeFetcherAgent
    # - Clone/fetch repository using GitPython
    # - If PR scan: fetch PR diff and changed files
    # - If project scan: fetch all relevant source files
    # - Handle authentication and access permissions
    # - Filter files by supported languages (Python, Java, Kotlin)
```

## Testing

The module includes comprehensive unit tests covering:

- **State Management**: GraphState creation and validation
- **Node Functions**: Individual node logic and error handling
- **Conditional Edges**: Workflow routing logic
- **Graph Compilation**: End-to-end graph setup
- **Integration Scenarios**: Workflow structure validation

Run tests with:

```bash
python -m pytest tests/core_engine/test_orchestrator.py -v
```

Current test coverage: **83%** (22 tests passing)

## Development Status

### ✅ Completed

- [x] GraphState model definition
- [x] All workflow node functions (placeholder implementations)
- [x] Conditional edge logic
- [x] Error handling workflow
- [x] Graph compilation and setup
- [x] Comprehensive unit tests
- [x] Documentation and examples

### 🔄 Next Steps

The orchestrator is ready for agent integration. The next development phase involves:

1. **CodeFetcherAgent**: Replace placeholder code fetching with GitPython implementation
2. **ASTParsingAgent**: Integrate Tree-sitter for actual AST parsing
3. **StaticAnalysisAgent**: Implement rule-based analysis engine
4. **LLMOrchestratorAgent**: Add LLM integration for semantic analysis
5. **ReportingAgent**: Enhance report generation with structured output

### 🔗 Integration Points

Each node function is designed to be easily replaceable with actual agent implementations:

- **Consistent Interface**: All nodes follow the same `(state: GraphState) -> Dict[str, Any]` pattern
- **Error Handling**: Built-in error propagation and handling
- **State Management**: Centralized state updates through return values
- **Logging**: Comprehensive logging for debugging and monitoring

## Configuration

The orchestrator uses the global settings from `config/settings.py`:

```python
from config.settings import settings

# Access configuration in node functions
llm_provider = settings.llm_provider
supported_languages = settings.supported_languages
```

## Error Handling

The workflow includes robust error handling:

- **Node-Level Errors**: Each node catches exceptions and sets error state
- **Workflow-Level Errors**: Conditional edges route to error handling node
- **Error Reports**: Structured error information in final output
- **Graceful Degradation**: Partial results preserved when possible

## Logging

All workflow steps include detailed logging:

```python
import logging
logger = logging.getLogger(__name__)

# Configure logging level
logging.basicConfig(level=logging.INFO)
```

## Performance Considerations

- **State Efficiency**: Minimal state copying between nodes
- **Memory Management**: Large data (ASTs, code) stored efficiently
- **Async Support**: Ready for async agent implementations
- **Checkpointing**: LangGraph supports workflow checkpointing for long-running tasks

## Contributing

When adding new agents or modifying the workflow:

1. **Maintain Interface**: Keep the `(state: GraphState) -> Dict[str, Any]` pattern
2. **Add Tests**: Include unit tests for new functionality
3. **Update Documentation**: Document new features and integration points
4. **Error Handling**: Ensure proper error propagation
5. **Logging**: Add appropriate logging statements 