# 👁️ AgentLens

[![PyPI Version](https://img.shields.io/pypi/v/agentlens-ui.svg?style=flat-square&logo=pypi&label=PyPI)](https://pypi.org/project/agentlens-ui/)
[![Python Versions](https://img.shields.io/pypi/pyversions/agentlens-ui.svg?style=flat-square&logo=python)](https://pypi.org/project/agentlens-ui/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

> ⚡️ **AgentLens** is an ultra-lightweight, zero-config, local-first observability and execution trace visualizer built specifically for multi-agent autonomous frameworks (CrewAI, LangGraph, AutoGen, and custom LLM workflows).

---

## 💡 Why AgentLens?

Cloud telemetry platforms (LangSmith, Phoenix, Datadog) require external API keys, introduce network latency, and store your agent thoughts and prompts on third-party servers.

**AgentLens runs 100% locally on your machine**:
- **0 ms Network Overhead**: Traces write locally to an embedded SQLite database using **WAL (Write-Ahead Logging)** mode.
- **Async & Thread-Safe**: Built on Python `contextvars` to reliably reconstruct nested parent-child call trees across coroutines and worker threads.
- **Zero Serialization Crashes**: Features a bulletproof fallback serialization barrier that gracefully handles non-serializable objects (generators, Pydantic models, binary blobs).
- **Embedded Web UI**: Single-command local dashboard (`agentlens ui`) with live polling, waterfall call trees, latency metrics, and syntax-highlighted JSON forensic inspection.

---

## 🚀 Quickstart

### 1. Installation

Install the engine via pip:
```bash
pip install agentlens-ui
```

### 2. Instrument Your Multi-Agent Code

Add the `@trace` decorator to your agents, tools, or task functions:

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

For programmatic logging (e.g. CrewAI step callbacks, LangChain event hooks):
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

### 3. Launch the Dashboard

Run the global CLI command in your project terminal:
```bash
agentlens ui
```

Open your browser at **`http://localhost:8000`** to view live waterfall traces, execution latency, and step-by-step agent reasoning!

---

## 🧩 Framework Integrations

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

## ⚙️ Configuration & Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `AGENTLENS_DB_PATH` | `./agentlens.db` | Absolute or relative path to the SQLite telemetry database file. |

To store telemetry in a centralized location across multiple projects:
```bash
export AGENTLENS_DB_PATH=~/.agentlens/traces.db
```

---

## 🏛️ Deep Technical Architecture

For an exhaustive technical audit of how AgentLens operates under the hood, read the [Staff Software Engineer Architectural Review](ARCHITECTURAL_REVIEW.md):
- **Lineage Mechanics**: Causal parent-child call graph resolution via `contextvars`.
- **Concurrency & WAL Mode**: Lockless readers, busy timeout queuing (`timeout=10.0`), and descriptor cleanup (`contextlib.closing`).
- **Serialization Boundary**: Two-tier safety mechanisms intercepting un-serializable models.
- **Comparative Analysis**: Performance benchmarks against cloud telemetry collectors.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
