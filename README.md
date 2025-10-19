# 🤖 ATOS - Agentic Task Orchestrator with Standardized Tooling

> **A $0 multi-agent system that thinks, decomposes, and executes complex software projects using local LLMs**

![Project Status](https://img.shields.io/badge/status-in--development-yellow)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 What is ATOS?

ATOS is an **asynchronous multi-agent orchestration system** that takes a high-level goal (like "Build a price-tracking SaaS") and:

1. **Decomposes** it into concrete tasks (design, code, test, deploy)
2. **Routes** tasks to specialized AI agents based on complexity
3. **Executes** tasks in parallel when possible (simple tasks) or sequentially (complex tasks)
4. **Self-debugs** failed code using reflection loops
5. **Orchestrates** operations through custom n8n workflows

**The Innovation:** Instead of one large model doing everything, ATOS uses a **pool of small, specialized models** (1-7B parameters) that dynamically load/unload based on task requirements — making it runnable on consumer hardware (4GB VRAM).

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  USER INPUT: "Build a price-tracking SaaS"              │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌────────────────────────────────────────────────────────┐
│  ORCHESTRATOR (Qwen2.5:7B - Always Loaded)            │
│  • Decomposes goal into tasks                         │
│  • Classifies: Simple | Medium | Complex              │
│  • Coordinates agent pools                            │
└────────────────────┬────────────────────────────────────┘
                     ↓ (sends task queue)
┌────────────────────────────────────────────────────────┐
│  n8n WORKFLOW ENGINE (Task Router)                     │
│  • In-memory task queue                                │
│  • Routes by complexity                                │
│  • Aggregates results                                  │
└──────┬─────────────────┬───────────────────┬───────────┘
       ↓                 ↓                   ↓
┌─────────────┐   ┌─────────────┐   ┌──────────────────┐
│ AGENT POOL A│   │ AGENT POOL B│   │ SPECIALIST CODER │
│ (Simple)    │   │ (Medium)    │   │ (Complex)        │
├─────────────┤   ├─────────────┤   ├──────────────────┤
│ 3x 1-3B     │   │ 1x 3-7B     │   │ 1x 7B Coder      │
│ models      │   │ model       │   │ model            │
│             │   │             │   │                  │
│ • File I/O  │   │ • API calls │   │ • Algorithms     │
│ • Parsing   │   │ • DB queries│   │ • Debug loops    │
│ • Configs   │   │ • Workflows │   │ • Full modules   │
└─────────────┘   └─────────────┘   └──────────────────┘
       ↓                 ↓                   ↓
       └─────────────────┴───────────────────┘
                         ↓
              ┌──────────────────────┐
              │  RESULT AGGREGATOR   │
              │  (n8n node)          │
              └──────────────────────┘
                         ↓
              ┌──────────────────────┐
              │  FINAL OUTPUT        │
              │  • Code repo         │
              │  • Deployment URL    │
              │  • Execution logs    │
              └──────────────────────┘
```

---

## 🎓 Why This Project Exists

**Learning Goals:**
- ✅ **Agentic Systems:** Build LLM-based agents with reasoning loops
- ✅ **Async Orchestration:** Coordinate multiple models working in parallel
- ✅ **VRAM Management:** Dynamically load/unload models on constrained hardware
- ✅ **MCP Protocol:** Design standardized tool interfaces
- ✅ **n8n Custom Nodes:** Extend workflow automation with TypeScript
- ✅ **Self-Debugging:** Implement reflection loops for code validation
- ✅ **Production Patterns:** Message queues, agent pools, observability

**This is NOT a toy project.** It's a production-grade architecture compressed to run on a laptop.

---

## 🗂️ Repository Structure

```
atos/
├── README.md                          # You are here
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package setup
├── .gitignore                        # Ignore models, logs, temp files
├── .env.example                      # Environment variables template
│
├── docs/                             # Project documentation
│   ├── architecture.md               # Deep dive into system design
│   ├── model_selection.md            # Why these models were chosen
│   ├── build_log.md                  # Daily build progress (your journal!)
│   └── troubleshooting.md            # Common errors and fixes
│
├── config/                           # Configuration files
│   ├── models.yaml                   # Model definitions and VRAM limits
│   ├── agents.yaml                   # Agent pool configurations
│   └── n8n_workflows.json            # n8n workflow exports
│
├── src/                              # Main source code
│   ├── __init__.py
│   │
│   ├── core/                         # Core orchestration logic
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # Main orchestrator (goal decomposer)
│   │   ├── task_classifier.py        # Classify tasks by complexity
│   │   └── result_aggregator.py      # Combine agent outputs
│   │
│   ├── agents/                       # Agent management
│   │   ├── __init__.py
│   │   ├── agent_pool_manager.py     # Load/unload models, VRAM tracking
│   │   ├── agent_executor.py         # Execute tasks with specific agents
│   │   └── models.py                 # Pydantic models for agents/tasks
│   │
│   ├── tools/                        # MCP Tool Servers
│   │   ├── __init__.py
│   │   ├── filesystem_server.py      # File read/write operations
│   │   ├── code_runner_server.py     # Execute pytest, return results
│   │   └── workflow_server.py        # Trigger n8n workflows
│   │
│   ├── langgraph/                    # LangGraph state machines
│   │   ├── __init__.py
│   │   ├── decompose_graph.py        # Goal → Tasks state machine
│   │   ├── debug_loop_graph.py       # Self-debugging reflection loop
│   │   └── states.py                 # State definitions (TypedDict)
│   │
│   ├── n8n_integration/              # n8n communication
│   │   ├── __init__.py
│   │   ├── webhook_client.py         # Send tasks to n8n
│   │   └── result_parser.py          # Parse n8n responses
│   │
│   └── observability/                # Logging and tracing
│       ├── __init__.py
│       ├── langsmith_tracer.py       # LangSmith integration
│       ├── wandb_logger.py           # W&B metrics
│       └── logger.py                 # Standard Python logging
│
├── n8n/                              # n8n custom nodes (TypeScript)
│   ├── package.json
│   ├── tsconfig.json
│   ├── nodes/
│   │   ├── ATOSAgentRouter/
│   │   │   ├── ATOSAgentRouter.node.ts      # Routes tasks to agents
│   │   │   └── ATOSAgentRouter.node.json
│   │   ├── ATOSResultAggregator/
│   │   │   ├── ATOSResultAggregator.node.ts
│   │   │   └── ATOSResultAggregator.node.json
│   │   └── ATOSDeploy/
│   │       ├── ATOSDeploy.node.ts           # Deploy to platforms
│   │       └── ATOSDeploy.node.json
│   └── credentials/
│       └── ATOSApi.credentials.ts
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_agent_pool.py
│   │   ├── test_orchestrator.py
│   │   └── test_tools.py
│   ├── integration/
│   │   ├── test_full_workflow.py
│   │   └── test_n8n_integration.py
│   └── fixtures/
│       └── sample_goals.json         # Test cases
│
├── examples/                         # Usage examples
│   ├── 01_tracer_bullet.py          # Simplest end-to-end test
│   ├── 02_single_agent.py           # One agent, one task
│   ├── 03_agent_pool.py             # Multiple agents in parallel
│   └── 04_full_orchestration.py     # Complete ATOS workflow
│
├── scripts/                          # Utility scripts
│   ├── setup_ollama.sh              # Pull all required models
│   ├── check_vram.py                # Monitor GPU memory usage
│   ├── test_n8n.sh                  # Verify n8n is running
│   └── cleanup.sh                   # Unload all models, clear cache
│
├── cli/                              # Command-line interface
│   ├── __init__.py
│   ├── main.py                      # CLI entry point
│   └── commands/
│       ├── build.py                 # `atos build "goal"`
│       ├── status.py                # `atos status`
│       └── debug.py                 # `atos debug <task_id>`
│
└── logs/                             # Runtime logs (not in git)
    ├── orchestrator.log
    ├── agents/
    │   ├── pool_a.log
    │   ├── pool_b.log
    │   └── specialist.log
    └── n8n/
        └── workflows.log
```

---

## 🧩 Core Components Explained

### 1. **Orchestrator** (`src/core/orchestrator.py`)
**What it does:** The "director" that receives user goals and breaks them into tasks.

**Key responsibilities:**
- Parse user input ("Build a todo app")
- Use Qwen2.5:7B to decompose into specific tasks
- Classify each task as Simple/Medium/Complex
- Send task queue to n8n

**Models used:** Qwen2.5:7B-Instruct (always loaded, 4GB VRAM)

---

### 2. **Agent Pool Manager** (`src/agents/agent_pool_manager.py`)
**What it does:** The "VRAM traffic controller" that loads/unloads models.

**Key responsibilities:**
- Track available VRAM (4GB limit)
- Load appropriate agents for task type
- Execute tasks in parallel (simple) or sequential (complex)
- Unload models to free memory

**Challenge:** Your 4GB VRAM can't fit multiple 7B models simultaneously, so this component must intelligently swap them.

---

### 3. **MCP Tool Servers** (`src/tools/`)
**What they do:** Standardized APIs that agents call to perform operations.

**Tools:**
- `filesystem_server.py` - Read/write files (for generated code)
- `code_runner_server.py` - Execute pytest, return pass/fail
- `workflow_server.py` - Trigger n8n workflows (deployments, notifications)

**Why:** Agents shouldn't directly touch the filesystem or APIs — tools provide safe, logged interfaces.

---

### 4. **LangGraph State Machines** (`src/langgraph/`)
**What they do:** Define agent reasoning flows with loops.

**Graphs:**
- `decompose_graph.py` - Goal → Task list
- `debug_loop_graph.py` - Code → Test → (if fail) Reflect → Fix → Test (repeat)

**Why LangGraph:** Because agents need to "think" in steps (Chain-of-Thought) and retry on failure.

---

### 5. **n8n Custom Nodes** (`n8n/nodes/`)
**What they do:** Extend n8n with ATOS-specific operations.

**Custom nodes:**
- `ATOSAgentRouter` - Receives tasks, routes to agent pools via API
- `ATOSResultAggregator` - Combines outputs from multiple agents
- `ATOSDeploy` - Deploys code to platforms (Heroku, GitHub Pages)

**Why custom nodes:** n8n's default nodes don't understand agent pools or VRAM management.

---

## 🚀 Quick Start

### Prerequisites
- **Python:** 3.10+
- **Node.js:** 18+
- **Ollama:** Installed and running
- **CUDA:** If using NVIDIA GPU (optional but recommended)
- **Storage:** 50GB free (for models)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/atos.git
cd atos

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Pull required models (will take 20-30 min)
bash scripts/setup_ollama.sh

# 5. Install n8n custom nodes
cd n8n
npm install
npm run build
npm link

# 6. Start n8n
npx n8n start

# 7. Copy environment variables
cp .env.example .env
# Edit .env with your settings
```

### First Test (Tracer Bullet)

```bash
# Run the simplest end-to-end test
python examples/01_tracer_bullet.py

# Expected output:
# 🧠 Loading orchestrator (Qwen2.5:7B)...
# ✅ Model loaded | VRAM: 4.1GB
# 🎯 Goal: Write a Python function to add two numbers
# 📝 Response: [model generates code]
# ✅ Tracer bullet complete!
```

If this works, your environment is ready! 🎉

---

## 📈 Build Progress Tracker

Track your journey through the project phases:

### Phase 1: Foundation (Weeks 1-2) 🔨
- [ ] Repository structure created
- [ ] Ollama models pulled (6 models)
- [ ] Tracer bullet #1: Single model call works
- [ ] Tracer bullet #2: Task decomposition works
- [ ] Agent Pool Manager skeleton implemented
- [ ] VRAM tracking working (`nvidia-smi` integration)

### Phase 2: Agent Orchestration (Weeks 3-4) 🤖
- [ ] Agent pool loading/unloading works
- [ ] Simple task pool (3x small models) executes in parallel
- [ ] Medium task pool (1x 3-7B model) executes sequentially
- [ ] Complex task pool (1x 7B coder) with orchestrator swap
- [ ] LangGraph decompose graph implemented
- [ ] MCP filesystem tool server working

### Phase 3: Self-Debugging (Weeks 5-6) 🔧
- [ ] Code runner tool server implemented
- [ ] Pytest execution and parsing works
- [ ] LangGraph debug loop graph implemented
- [ ] Reflection loop: fail → analyze → fix → retry
- [ ] AST parsing for syntax validation
- [ ] Test coverage for generated code

### Phase 4: n8n Integration (Weeks 7-8) ⚙️
- [ ] n8n development environment set up
- [ ] ATOSAgentRouter custom node created
- [ ] Task routing workflow implemented
- [ ] ATOSResultAggregator node created
- [ ] Webhook communication working
- [ ] Error handling in n8n workflows

### Phase 5: Operations (Weeks 9-10) 🚀
- [ ] ATOSDeploy node for Heroku
- [ ] GitHub integration (push code)
- [ ] Workflow trigger tool server
- [ ] End-to-end: goal → code → deploy
- [ ] Deployment verification workflow

### Phase 6: Observability (Weeks 11-12) 📊
- [ ] LangSmith tracing integrated
- [ ] W&B logging for metrics
- [ ] CLI interface (`atos build "goal"`)
- [ ] Status monitoring (`atos status`)
- [ ] Debug commands (`atos debug <task_id>`)

### Phase 7: Polish & Documentation (Week 13+) ✨
- [ ] Error messages improved
- [ ] User documentation written
- [ ] Example projects created
- [ ] Performance optimization
- [ ] Demo video recorded

---

## 🎯 Current Status

**Phase:** Foundation (Week 1)  
**Last Updated:** [Your Date]  
**Current Focus:** Setting up repository structure and pulling models

**Next Milestones:**
1. Get Ollama working with one model
2. Write tracer bullet #1 (single model call)
3. Implement basic AgentPoolManager

**Blockers:**
- [ ] None yet (hopefully!)

*(Update this section as you progress)*

---

## 🧪 Testing Strategy

### Unit Tests
```bash
pytest tests/unit/ -v
```
Test individual components in isolation (agent manager, orchestrator, tools).

### Integration Tests
```bash
pytest tests/integration/ -v
```
Test multi-component workflows (agent pool + n8n, orchestrator + tools).

### End-to-End Tests
```bash
python examples/04_full_orchestration.py
```
Full user journey: goal → decomposed → executed → deployed.

---

## 🛠️ Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Orchestrator** | Qwen2.5:7B | Best 7B reasoning model, 128K context |
| **Coders** | Qwen2.5-Coder:7B/3B | Top code generation models |
| **Simple Agents** | Phi-3.5:3.8B, Gemma2:2B | Lightweight, specialized |
| **Agent Framework** | LangGraph | State machines for reasoning loops |
| **Tool Protocol** | MCP (via FastAPI) | Standardized agent-tool interface |
| **Orchestration** | n8n (self-hosted) | Workflow automation + custom nodes |
| **Observability** | LangSmith + W&B | LLM tracing + metrics |
| **Testing** | pytest | Code validation in debug loops |
| **Language** | Python 3.10+ | Main application |
| **Custom Nodes** | TypeScript | n8n node development |

---

## 💾 Resource Requirements

**Minimum Specs:**
- GPU: 4GB VRAM (RTX 3050, GTX 1650)
- RAM: 16GB
- Storage: 50GB
- CPU: 6+ cores

**Recommended Specs:**
- GPU: 6-8GB VRAM (RTX 3060)
- RAM: 32GB
- Storage: 100GB SSD
- CPU: 8+ cores

---

## 🐛 Common Issues & Solutions

### Model Loading Fails
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Verify model is pulled
ollama list

# Check VRAM usage
nvidia-smi
```

### VRAM Overflow
```bash
# Monitor in real-time
watch -n 1 nvidia-smi

# Force unload all models
python scripts/cleanup.sh
```

### n8n Won't Start
```bash
# Check port availability
lsof -i :5678

# Restart n8n
pkill -f n8n
npx n8n start
```

See `docs/troubleshooting.md` for full list.

---

## 📚 Learning Resources

**Before you code, read:**
- [Ollama Python Docs](https://github.com/ollama/ollama-python)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/tutorials/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [n8n Node Creation](https://docs.n8n.io/integrations/creating-nodes/)

**Concepts to understand:**
- Async/await in Python
- State machines (LangGraph)
- Dependency injection (FastAPI)
- TypeScript classes (n8n nodes)
- VRAM vs RAM

---

## 🎓 Development Philosophy

This project follows **"Learn by Building Hard Things"**:

1. **No spoon-feeding** - Figure it out, break it, fix it
2. **Documentation first** - Read docs before asking
3. **Test in isolation** - REPL is your friend
4. **Commit often** - So you can revert when you fuck up
5. **Debug systematically** - Print everything, read errors
6. **Embrace struggle** - Confusion means you're learning

**Mantra:** "If it's easy, I'm not learning."

---

## 🤝 Contributing

This is a personal learning project, but feedback welcome!

**If you want to learn alongside:**
1. Fork this repo
2. Follow the build phases
3. Share your struggles (and solutions!) in Issues
4. Document your unique insights

**What NOT to do:**
- Don't submit "just use X library" PRs (defeats the learning purpose)
- Don't refactor for "cleanliness" (clarity > elegance when learning)

---

## 📝 Build Log

Keep a daily journal in `docs/build_log.md`:

```markdown
## Day 1 - [Date]
**Goal:** Set up repository structure  
**What I learned:** How to organize a multi-language monorepo  
**Blockers:** None  
**Tomorrow:** Pull Ollama models and test first model call

## Day 2 - [Date]
**Goal:** Get Qwen2.5:7B running  
**What I learned:** Q4_K_M quantization reduces VRAM by 75%  
**Blockers:** Model loading takes 8 seconds (normal?)  
**Tomorrow:** Write tracer bullet script
```

This is YOUR learning log. Be honest about struggles.

---

## 🔮 Future Extensions

After completing the base project:

1. **Polymathic Engine Integration** - Add knowledge graph for innovation
2. **Multi-GPU Support** - Scale to larger models
3. **Web UI** - React dashboard for monitoring
4. **Cloud Deployment** - Run orchestrator on server, agents on edge
5. **Fine-tuned Agents** - Train specialized micro-models

---

## 📄 License

MIT License - See `LICENSE` file

---

## 🙏 Acknowledgments

**Built on the shoulders of:**
- Ollama team (local LLM runtime)
- Qwen team (amazing open models)
- LangChain/LangGraph (agent frameworks)
- n8n team (workflow automation)

**Inspired by:**
- The idea that $0 and consumer hardware can run production-grade AI systems
- The belief that struggling through hard projects is the best teacher

---

## 📧 Contact

**Questions about the project?** Open an issue.  
**Want to share your learning?** Post in Discussions.  
**Found a bug?** You probably caused it. Debug it. Then tell me how. 😉

---

**Remember:** This README is your north star. When lost, come back here. When stuck, read the relevant section. When you want to give up, remember why you started.

**You're not building a calculator. You're building a distributed AI system. It's supposed to be hard.**

Now go write some code. 🚀
