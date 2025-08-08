# env_sanity_check.py

import os
import torch

# Agentic / LLM stack
import langgraph
import autogen
import transformers
import chromadb
import sentence_transformers

# Data stack
import duckdb
import pyarrow
import pandas as pd

# Simulation / ML stack
import mesa
import optuna
import faiss

# Monitoring / Ops
import mlflow
import wandb
import dotenv

# Database connectors
import pymongo
from arango import ArangoClient

# Core check
def main():
    print("="*40)
    print("🚀 Universal AI Env Sanity Check")
    print("="*40)

    # Check torch device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"✅ Torch is using: {device}")
    if device.type == "cuda":
        print(f"🎯 GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️ GPU not available. Running on CPU.")

    # Run a quick tensor operation
    a = torch.randn(1000, 1000, device=device)
    b = torch.randn(1000, 1000, device=device)
    c = torch.matmul(a, b)
    print("✅ Matrix multiplication succeeded")

    # Langchain family check
    from langchain_core.prompts import ChatPromptTemplate
    print("✅ LangGraph and LangChain imports OK")

    # Chromadb
    client = chromadb.Client()
    print("✅ ChromaDB in-memory client created")

    # Sentence transformer test
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode("Test sentence")
    print("✅ SentenceTransformer embedded a sentence")

    print("🎉 All critical packages loaded and working!\n")

if __name__ == "__main__":
    main()