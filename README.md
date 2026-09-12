# 👁️ AgentLens UI

**Zero-config, local observability UI for multi-agent systems.**

Building multi-agent systems with frameworks like CrewAI and LangGraph often results in unreadable terminal vomit. AgentLens is a lightweight, local-first visual debugger that intercepts agent thoughts, tool executions, and state handoffs, rendering them into a beautiful, real-time timeline—all without leaving your local environment.

No Node.js. No Docker. No cloud accounts. Just Python.

---

## 🚀 Why AgentLens?

*   **Zero Setup Tax:** Installs via `pip` and runs instantly. No `docker-compose` or API keys required.
*   **Privacy First:** All logs are written to a local thread-safe SQLite database (`agentlens.db`). Your proprietary prompts and API keys never leave your machine.
*   **Payload Inspector:** Automatically captures and formats massive, nested JSON payloads so you can easily spot context blow-ups and hallucinated tool arguments.
*   **Framework Agnostic:** Works seamlessly with CrewAI, LangChain, or any custom Python agent loop.

---

## 📦 Installation

AgentLens requires Python 3.9 or higher.

```bash
pip install agentlens-ui
```

⚡ Quick Start
1. Trace Your AgentsDrop the @trace decorator onto your agent functions, tools, or orchestrators to start logging execution steps.
2. Python
  from agentlens_ui.core import trace
  import time

# Trace a tool
@trace("Web_Search_Tool")
def search_web(query: str):
    time.sleep(1.5)
    return {"status": "success", "data": "AI agents are replacing traditional workflows."}

# Trace an orchestrator or main execution
@trace("Main_Orchestrator")
def run_agent_pipeline():
    search_web("multi-agent orchestration trends")
    return "Pipeline finished."

if __name__ == "__main__":
    run_agent_pipeline()
    
2. Launch the Dashboard
3. Open your terminal and run the global CLI command:
   agentlens ui
4. Navigate to http://localhost:8000 in your browser. The dashboard will auto-refresh and display your multi-agent execution in real-time.

🏗️ Architecture
AgentLens is engineered for strict environment isolation and high concurrency:
1. Backend: Powered by FastAPI.  
2. Storage: Utilizes Python's native sqlite3 with Write-Ahead Logging (WAL) and ContextVar scoping to safely handle highly concurrent, async multi-agent writes without locking your database.  
3. Frontend: A single-file, zero-dependency Vanilla CSS/JS application. We eliminated React and Webpack so Python developers don't have to pay the "Node.js Tax" just to view their logs.  

👨‍💻 Author
Built by Kushal Hiremath.

📄 License
This project is licensed under the MIT License
