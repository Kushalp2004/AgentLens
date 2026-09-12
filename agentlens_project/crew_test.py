import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from agentlens_ui.core import trace, log_trace

# Load your GOOGLE_API_KEY from the .env file
load_dotenv() 

# 1. Use CrewAI's native LLM wrapper (LiteLLM) instead of LangChain
# The "gemini/" prefix tells the engine exactly how to route the request
gemini_llm = LLM(
    model="gemini/gemini-3.8-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# --- 1. SPYING ON TOOLS WITH AGENTLENS ---
@tool("Web_Search")
@trace("Web_Search_Tool")
def search_web(query: str) -> str:
    """Useful for searching the internet for recent data."""
    import time; time.sleep(1.5) 
    return f"Found data for '{query}': AI agents are replacing traditional software workflows."

# --- 2. SPYING ON AGENT HANDOFFS ---
def agent_callback(step_output):
    log_trace(
        agent_name="CrewAI_Orchestrator",
        step_type="THOUGHT",
        content="Agent completed a reasoning step.",
        details={"output": step_output.thought}
    )

# --- 3. THE CREWAI SETUP ---
researcher = Agent(
    role='Senior Tech Researcher',
    goal='Uncover the latest trends in Agentic AI',
    backstory='You are an elite Silicon Valley researcher.',
    tools=[search_web],
    verbose=True,
    llm=gemini_llm,  # <-- Passing the native CrewAI LLM object
    step_callback=agent_callback
)

writer = Agent(
    role='Tech Blogger',
    goal='Draft an engaging blog post based on the research',
    backstory='You write highly engaging, technical blog posts.',
    verbose=True,
    llm=gemini_llm,  # <-- Passing the native CrewAI LLM object
    step_callback=agent_callback
)

research_task = Task(
    description='Research the current state of multi-agent orchestration frameworks.',
    expected_output='A bulleted list of 3 key trends.',
    agent=researcher
)

write_task = Task(
    description='Using the research, write a 2-paragraph blog post intro.',
    expected_output='A clean, formatted markdown blog post.',
    agent=writer
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential 
)

if __name__ == "__main__":
    print("🚀 Starting real CrewAI multi-agent run with Gemini 3.8 Flash...")
    
    @trace("Crew_Execution")
    def run_crew():
        return crew.kickoff()
    
    result = run_crew()
    print("\n✅ Crew Finished. Open AgentLens to see the trace.")