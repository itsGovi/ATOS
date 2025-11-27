import time
import os
from dotenv import load_dotenv 
from openai import OpenAI

load_dotenv()

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1" 

# TEAM CONFIGURATION
# UPDATED TEAM: Optimized for Uptime & Speed
ATOS_TEAM = {
    "Orchestrator (Grok 4.1)": "x-ai/grok-4.1-fast:free",    
    "Coder (Kwaipilot)": "kwaipilot/kat-coder-pro:free",
    "Small Agent (GLM 4.5 Air)": "z-ai/glm-4.5-air:free"
}


TEST_PROMPT = [
    {
        "role": "user",
        "content": """
GOAL: Create a fault-tolerant, asynchronous web crawler in Python.

SCENARIO:
You need to crawl 10,000 pages from a site that is flaky (random 500 errors) and rate-limited (max 5 req/sec).

REQUIREMENTS:
1. Architecture: Use `aiohttp` and `asyncio`.
2. Pattern: Implement a "Producer-Consumer" queue pattern. One worker fetches URLs, multiple workers process HTML.
3. Resilience: Implement an exponential backoff decorator for 5xx errors.
4. State: Save progress to SQLite so we can kill the script and resume 100% losslessly.

INSTRUCTION FOR CODER:
Write the complete, runnable Python code. Focus on the `crawl_worker` function and the SQLite state management.
"""
    }
]

# ------------------------------------------------------------------
# THE BENCHMARK
# ------------------------------------------------------------------
def run_benchmark():
    print(f"🚀 Starting Connectivity Test to: {BASE_URL}")
    if not API_KEY:
        print("❌ ERROR: API_KEY not found. Did you create the .env file?")
        return
        
    print(f"🔑 Key loaded: {API_KEY[:4]}...****")
    print("-" * 50)

    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )

    results = []

    for role, model_id in ATOS_TEAM.items():
        print(f"\n📡 Testing {role} [{model_id}]...")
        
        start_time = time.time()
        
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=TEST_PROMPT,
                temperature=0.7,
                max_tokens=1000 
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            content = response.choices[0].message.content
            
            # Preview 200 chars to verify it's writing code
            preview_text = content[:200].replace('\n', ' ') if content else "No content"
            
            status = "✅ Success" if content else "❌ Empty"
            
            print(f"   ⏱️ Time Taken: {duration:.2f} seconds")
            print(f"   📝 Output preview: {preview_text}...")
            
            results.append({
                "role": role,
                "time": duration,
                "status": status
            })

        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
            results.append({
                "role": role,
                "time": 999.0,
                "status": "Failed"
            })

    # ------------------------------------------------------------------
    # REPORT CARD
    # ------------------------------------------------------------------
    print("\n" + "="*50)
    print("📊 BENCHMARK RESULTS")
    print("="*50)
    print(f"{'ROLE':<30} | {'STATUS':<10} | {'TIME (s)':<10}")
    print("-" * 55)
    
    for res in results:
        print(f"{res['role']:<30} | {res['status']:<10} | {res['time']:<10.2f}")

    print("="*50)

if __name__ == "__main__":
    run_benchmark()













from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# CONCEPT: Structured Interfaces
# ANALOGY: This is the "Contract" between your agents.
#          Grok (Orchestrator) promises to output a 'Plan' object.
#          Kat (Coder) promises to accept a 'Task' object.
#          If they break this promise, our code stops them before they crash the app.

class Task(BaseModel):
    """
    A single unit of work to be executed by an agent.
    """
    id: int = Field(description="Unique incremental ID for the task (1, 2, 3...)")
    name: str = Field(description="Short, action-oriented title (e.g., 'Write login.py')")
    description: str = Field(description="Detailed instructions for the agent who will do this task.")
    
    # This field routes the task to the right agent!
    # Simple -> Small Agent (Llama 3)
    # Complex -> Coder (Kwaipilot)
    complexity: Literal["Simple", "Medium", "Complex"] = Field(
        description="Estimated difficulty. Simple=Text changes, Complex=New logic/algorithms."
    )
    
    status: Literal["pending", "in_progress", "completed", "failed"] = "pending"
    file_dependencies: Optional[List[str]] = Field(default=[], description="List of files this task needs to read/edit.")

class Plan(BaseModel):
    """
    The Master Plan. The Orchestrator (Grok) outputs THIS object.
    """
    goal: str = Field(description="The user's original high-level goal.")
    tasks: List[Task] = Field(description="The list of tasks to execute, in order.")
    
    reasoning: str = Field(description="A brief explanation of why this breakdown was chosen.")