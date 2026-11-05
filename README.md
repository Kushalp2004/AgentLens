# AgentLens

[![PyPI Version](https://img.shields.io/pypi/v/agentlens-ui.svg?style=flat-square&logo=pypi&label=PyPI)](https://pypi.org/project/agentlens-ui/)
[![Python Versions](https://img.shields.io/pypi/pyversions/agentlens-ui.svg?style=flat-square&logo=python)](https://pypi.org/project/agentlens-ui/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

AgentLens is a lightweight, zero-configuration, local-first observability and execution trace visualizer built for multi-agent autonomous frameworks (CrewAI, LangGraph, AutoGen, and custom LLM workflows).

---

## Overview

Telemetry platforms often require external API keys, introduce network latency, and store agent thoughts and prompts on third-party servers.

AgentLens runs locally on your machine:
- **Zero Network Overhead**: Traces write locally to an embedded SQLite database using Write-Ahead Logging (WAL) mode.
- **Async and Thread-Safe**: Built on Python `contextvars` to reconstruct nested parent-child call trees across coroutines and worker threads.
- **Crash-Resilient Serialization**: Implements fallback serialization to handle non-serializable objects (generators, Pydantic models, binary payloads) without failing the host process.
- **Embedded Web UI**: Single-command local dashboard (`agentlens ui`) providing live polling, waterfall call trees, latency metrics, and formatted JSON inspection.

---

## Quickstart

### 1. Installation

Install via pip:
```bash
pip install agentlens-ui
```

### 2. Instrument Multi-Agent Workflows

Apply the `@trace` decorator to agent functions, tools, or task handlers:

```python
from agentlens_ui.core import trace

# Trace standalone tools
@trace("Web_Search_Tool")
def search_web(query: str):
    return f"Latest results for: {query}"

# Trace async or sync agent executions
@trace("Researcher_Agent")
async def run_agent(task_description: str):
    results = search_web("AI multi-agent orchestration")
    return f"Completed analysis with {results}"
```

For programmatic logging (such as CrewAI step callbacks or event listeners):
```python
from agentlens_ui.core import log_trace

def step_callback(step_output):
    log_trace(
        agent_name="CrewAI_Orchestrator",
        step_type="THOUGHT",
        content="Agent finished reasoning step.",
        details={"thought": step_output.thought}
    )
```

### 3. Launch Dashboard

Run the CLI command in your project directory:
```bash
agentlens ui
```

Navigate to `http://localhost:8000` to view waterfall traces, execution latency, and step-by-step reasoning logs.

---

## Framework Integrations

### CrewAI Integration Example

```python
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from agentlens_ui.core import trace, log_trace

# 1. Trace Custom Tools
@tool("Search_Tool")
@trace("Search_Tool")
def search(query: str) -> str:
    return "Fetched live trend data."

# 2. Trace Thought Callbacks
def agent_callback(step_output):
    log_trace(
        agent_name="CrewAI_Manager",
        step_type="THOUGHT",
        content="Agent completed thought step",
        details={"output": step_output.thought}
    )

# 3. Trace Full Execution
@trace("Crew_Execution")
def kickoff_crew():
    crew = Crew(
        agents=[...],
        tasks=[...],
        process=Process.sequential,
        step_callback=agent_callback
    )
    return crew.kickoff()

if __name__ == "__main__":
    kickoff_crew()
```

---

## Configuration

| Variable | Default | Description |
| :--- | :--- | :--- |
| `AGENTLENS_DB_PATH` | `./agentlens.db` | Absolute or relative path to the SQLite telemetry database file. |

To store telemetry in a centralized location across multiple projects:
```bash
export AGENTLENS_DB_PATH=~/.agentlens/traces.db
```

---

## Architecture

For an in-depth breakdown of system mechanics, refer to the [Architecture Review](agentlens_project/ARCHITECTURAL_REVIEW.md):
- **Lineage Mechanics**: Causal parent-child call graph resolution via `contextvars`.
- **Concurrency & WAL Mode**: Lockless readers, busy timeout queuing (`timeout=10.0`), and descriptor cleanup (`contextlib.closing`).
- **Serialization Boundary**: Multi-tiered fallback mechanisms for un-serializable models.
- **Comparative Analysis**: Performance benchmarks against cloud telemetry collectors.

---

## License

Distributed under the [MIT License](LICENSE).
