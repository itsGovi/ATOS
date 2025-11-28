"""
Benchmark script for testing multiple models against a shared prompt.
- Debug logging enabled.
- Saves full responses to disk (benchmark_outputs/).
- Type-hinted and defensive when extracting response content.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

# Load environment
load_dotenv()

# -----------------------
# Logging (DEBUG enabled)
# -----------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("benchmark")

# -----------------------
# Config
# -----------------------
API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
BASE_URL: str = "https://openrouter.ai/api/v1"

# OUTPUT DIRECTORY (your request)
OUTPUT_DIR = Path("/home/govi/Projects/ATOS/benchmarks_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "benchmark_results.json"

ATOS_TEAM: Dict[str, str] = {
    "Orchestrator (Grok 4.1)": "x-ai/grok-4.1-fast:free",
    "Coder (Kwaipilot)": "kwaipilot/kat-coder-pro:free",
    "Small Agent (LongCat Chat)": "meituan/longcat-flash-chat:free",
}

TEST_PROMPT: List[Dict[str, Any]] = [
    {
        "role": "user",
        "content": """
GOAL: Create a fault-tolerant, asynchronous web crawler in Python.

SCENARIO:
You need to crawl 10,000 pages from a site that is flaky (random 500 errors) 
and rate-limited (max 5 req/sec).

REQUIREMENTS:
1. Architecture: Use `aiohttp` and `asyncio`.
2. Pattern: Implement a "Producer-Consumer" queue pattern.
3. Resilience: Implement an exponential backoff decorator for 5xx errors.
4. State: Save progress to SQLite so we can kill the script and resume losslessly.

INSTRUCTION FOR CODER:
Write the complete, runnable Python code.
Focus on the crawl_worker() function and SQLite state management.
"""
    }
]


# ---------------------------------------------------------
# Utility: Extract content robustly
# ---------------------------------------------------------
def extract_content_from_response(response: Any) -> str:
    try:
        choices = getattr(response, "choices", None)
        if choices:
            first = choices[0]

            # response.choices[0].message.content
            if hasattr(first, "message"):
                content = getattr(first.message, "content", None)
                if isinstance(content, str):
                    return content

            # response.choices[0].text
            text = getattr(first, "text", None)
            if isinstance(text, str):
                return text

            # dict-like fallback
            if isinstance(first, dict):
                for key in ("content", "text"):
                    v = first.get(key)
                    if isinstance(v, str):
                        return v
                msg = first.get("message")
                if isinstance(msg, dict):
                    if isinstance(msg.get("content"), str):
                        return msg["content"]
    except Exception as exc:
        logger.debug("extract_content error: %s", exc)

    return ""


# ---------------------------------------------------------
# Benchmark Runner
# ---------------------------------------------------------
def run_benchmark() -> None:
    if not API_KEY:
        logger.error("Missing OPENROUTER_API_KEY in environment")
        return

    logger.info("Using API key: %s...****", API_KEY[:4])

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    all_results: Dict[str, Any] = {
        "timestamp": time.time(),
        "base_url": BASE_URL,
        "models": []
    }

    # -----------------------------
    # Loop through all 3 models
    # -----------------------------
    for role, model_id in ATOS_TEAM.items():
        logger.info("📡 Testing %s [%s]...", role, model_id)
        start = time.time()

        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=TEST_PROMPT,
                temperature=0.7,
            )

            duration = time.time() - start
            content = extract_content_from_response(response)
            preview = content[:200].replace("\n", " ") if content else "<no content>"

            logger.info("   ⏱️ Time: %.2f sec", duration)
            logger.info("   📝 Preview: %s", preview)

            # Store structured data for this model
            all_results["models"].append({
                "role": role,
                "model_id": model_id,
                "status": "success" if content else "empty",
                "duration_seconds": duration,
                "content_preview": preview,
                "content_full": content,
                "raw_response_repr": repr(response)[:2000],  # avoid megabytes
            })

        except Exception as exc:
            duration = time.time() - start
            logger.exception("   ❌ Failed for %s (%s): %s", role, model_id, exc)

            all_results["models"].append({
                "role": role,
                "model_id": model_id,
                "status": "error",
                "duration_seconds": duration,
                "error": str(exc),
            })

    # ---------------------------------------------------------
    # Save ONE structured JSON file for all models
    # ---------------------------------------------------------
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        logger.info("📦 Saved combined benchmark JSON → %s", OUTPUT_FILE)
    except Exception as e:
        logger.exception("Failed to write final benchmark output: %s", e)

    # ---------------------------------------------------------
    # Terminal Summary
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"{'ROLE':<30} | {'MODEL':<25} | {'STATUS':<10} | TIME (s)")
    print("-" * 70)

    for m in all_results["models"]:
        print(f"{m['role']:<30} | {m['model_id']:<25} | {m['status']:<10} | {m['duration_seconds']:.2f}")

    print("=" * 70)
    print(f"Results saved to:\n  {OUTPUT_FILE}\n")


# ---------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------
if __name__ == "__main__":
    run_benchmark()
