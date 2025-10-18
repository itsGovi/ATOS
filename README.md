# 🧠 Project 1 — Agentic CLI Debugging Assistant

> **Goal:** Build a robust, test-driven Command Line Interface (CLI) tool that fetches real-time data from an external API, processes it, and writes to a CSV file — with a built-in `--self-debug` mode that identifies and hints at common runtime errors.

---

## 📍 Table of Contents

1. [Project Overview](#-project-overview)
2. [Motivation](#-motivation)
3. [Architecture](#-architecture)
4. [Folder Structure](#-folder-structure)
5. [Setup & Installation](#-setup--installation)
6. [Usage](#-usage)
7. [Testing](#-testing)
8. [Debugging & Self-Debug Mode](#-debugging--self-debug-mode)
9. [Development Practices](#-development-practices)
10. [Future Improvements](#-future-improvements)
11. [Learnings](#-learnings)

---

## 🚀 Project Overview

This project simulates a **mini production-grade CLI application** with real-world developer workflows — API integration, structured logging, testing, debugging, CI/CD, and documentation.

You’ll build a CLI called **`fetcher`**, which:

* Fetches data from a public API (e.g., CoinDesk’s Bitcoin Price Index).
* Writes it to a CSV file in a clean, modular way.
* Includes a `--self-debug` flag that runs tests and maps common errors to actionable hints.

This is designed to teach:

* Clean code organization.
* Reading and understanding tracebacks.
* Writing automated tests before/after debugging.
* Building muscle memory for real-world debugging.

---

## 💡 Motivation

> “You don’t truly understand code until you can debug it.”

This project is your **debugging dojo** — it’s where you’ll get comfortable seeing red (errors) and calmly tracing the root cause. Instead of just ‘building features,’ you’ll develop habits that make you a **10x learner**:

* Write before you code (design-first thinking).
* Test before you assume (data over ego).
* Debug with intention (treat errors as feedback loops).

---

## 🧩 Architecture

| Layer               | File          | Purpose                                                      |
| ------------------- | ------------- | ------------------------------------------------------------ |
| **CLI Entry Point** | `cli.py`      | Handles command-line args and triggers logic.                |
| **API Layer**       | `api.py`      | Fetches and validates external data from APIs.               |
| **IO Layer**        | `io.py`       | Handles reading/writing files (CSV).                         |
| **Core Logic**      | `core.py`     | Central business logic (formatting, computation).            |
| **Debug Engine**    | `debugger.py` | Implements `--self-debug` by running tests programmatically. |
| **Config**          | `config.py`   | Stores constants, file paths, etc.                           |
| **Tests**           | `/tests`      | Unit + integration tests (pytest).                           |

---

## 🗂 Folder Structure

```
project1-cli/
│
├── fetcher/                       # main package
│   ├── __init__.py
│   ├── cli.py                      # command-line entrypoint
│   ├── api.py                      # handles API calls
│   ├── io.py                       # CSV writer/reader
│   ├── core.py                     # core logic & transformations
│   ├── debugger.py                 # self-debug feature
│   ├── config.py                   # constants, settings
│   └── utils.py                    # helper functions
│
├── tests/                         # unit + integration tests
│   ├── test_api.py
│   ├── test_io.py
│   ├── test_cli.py
│   └── test_integration.py
│
├── scripts/                       # failure injection scripts
│   ├── simulate_timeout.py
│   ├── simulate_json_error.py
│   └── simulate_permission_error.py
│
├── .github/workflows/ci.yml       # GitHub Actions CI
├── .pre-commit-config.yaml        # formatters + linters
├── requirements.txt               # dependencies
├── pyproject.toml                 # project meta + formatter setup
├── DEBUGGING.md                   # debugging guide
├── README.md                      # this file
└── LICENSE
```

---

## ⚙️ Setup & Installation

### Prerequisites

* Python 3.10+
* `pip`, `venv`, `git`

### Steps

```bash
# 1. Clone repo
git clone https://github.com/itsGovi/project1-cli.git
cd project1-cli

# 2. Setup virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run pre-commit hooks (optional)
pre-commit install
```

---

## 🧰 Usage

Run the CLI:

```bash
python -m fetcher.cli --output prices.csv
```

Check the CSV output:

```bash
cat prices.csv
```

Run the self-debug mode:

```bash
python -m fetcher.cli --self-debug
```

Example output:

```
[DEBUG] Running tests...
❌ test_api_timeout_failed
Hint → requests.exceptions.Timeout: Retry or mock this API call.
✅ test_io_valid_write
✅ test_cli_integration
```

---

## 🧪 Testing

Run all tests:

```bash
pytest -v
```

Run a specific test:

```bash
pytest tests/test_api.py::test_get_price_success
```

Generate coverage report:

```bash
pytest --cov=fetcher --cov-report=term-missing
```

---

## 🪲 Debugging & Self-Debug Mode

The `--self-debug` flag runs internal tests and maps common exceptions to plain-English hints.

**Example mappings:**

| Exception                     | Hint                                                 |
| ----------------------------- | ---------------------------------------------------- |
| `ModuleNotFoundError`         | Check import paths and PYTHONPATH.                   |
| `PermissionError`             | Verify file write permissions and paths.             |
| `requests.exceptions.Timeout` | Network timeout — retry or mock API.                 |
| `KeyError`                    | JSON key missing — handle schema changes gracefully. |
| `AssertionError`              | Test mismatch — inspect expected vs actual values.   |

> 💡 **Pro tip:** Treat every bug as a feedback loop, not a failure.

---

## 🧭 Development Practices

### 🧱 Code Hygiene

* Keep functions under 25 lines.
* Each module = single responsibility.
* Write docstrings (`Google-style`).
* Run formatters (`black`, `isort`) before commits.

### 🔄 Git Workflow

1. Create feature branch: `git checkout -b feature/add-debugger`
2. Commit frequently, small atomic commits.
3. Use descriptive messages (`feat: add retry logic for API`).

### 🧪 Testing Mindset

* Start with a failing test → fix → verify.
* Capture regressions (add tests for every bug you fix).
* Use mocks for APIs, not real calls.

### 🧰 Tools

* `pytest` — testing
* `black`, `flake8`, `isort` — formatting
* `pre-commit` — hooks
* `GitHub Actions` — CI/CD
* `logging` — runtime insights

---

## 🚧 Future Improvements

* Add retry & exponential backoff for API.
* Add `--compare` mode for multi-day CSV diffs.
* Add dashboard (Streamlit) to visualize data.
* Extend `--self-debug` to auto-fix simple import errors.

---

## 🧠 Learnings

* How to read and act on stack traces calmly.
* How to design layered architecture in Python.
* How to structure tests for maintainability.
* How CI/CD and pre-commit reduce human friction.
* How writing a self-debug tool changes your debugging intuition.

---

## 🪄 Final Thought

> "You can copy code, but you can’t copy intuition — this repo is about building that intuition."
