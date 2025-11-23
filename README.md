#  QodeFix: AI Code Remediation Microservice

Local LLM • FastAPI • Secure Code Fixing • Optional RAG

This project implements an AI Remediation Microservice.
It provides a local microservice that takes a vulnerable code snippet and returns:

A secure fixed version

A unified diff of changes

A clear vulnerability explanation

Model name, token usage, and latency

The service runs entirely on local inference using DeepSeek-Coder 1.3B (or any HF model), supports CPU-only, and includes an optional RAG system powered by FAISS and SentenceTransformers.

## System Flow Diagram

![Flow Diagram](qodefixer.drawio (1).png)

*(Refer to the included PNG qodefixer.drawio (1).png)*

---

## Features
 Local LLM Inference (Transformers)

Runs DeepSeek-Coder or any open-source coder model locally

Pure CPU support

No external paid APIs

Stable generation with structured prompts

 FastAPI Microservice

Endpoint: POST /local_fix

Well-defined request + response schema

 Security-Focused Prompt Engineering

Strict output markers ensure consistent extraction:

<<<FIXED_CODE>>> ... <<<END_FIXED_CODE>>>
<<<EXPLANATION>>> ... <<<END_EXPLANATION>>>

 Diff Generation

Clean unified diff using Python’s difflib

 Logging & Metrics

Token counts

Latency (ms)

Model used

Recorded in logs/metrics.csv

 Mini-RAG (Retrieval-Augmented Generation)

Uses FAISS + embeddings

Reads security recipes from recipes/

Automatically selects the best guideline

Improves consistency and correctness of fixes

## Installation
Create and activate venv
python -m venv .venv
.\.venv\Scripts\activate     # Windows

Install dependencies
pip install -r requirements.txt

First-run model download

Transformers will download DeepSeek-Coder (≈2.7 GB) automatically.

Running the Service
uvicorn app.main:app --reload

Interactive API Documentation

Open:

 http://127.0.0.1:8000/docs

Use the “Try it out” button on /local_fix.

Example request:

{
  "language": "java",
  "cwe": "CWE-89",
  "code": "String query = \"SELECT * FROM users WHERE username = '\" + userInput + \"'\";"
}

Command-Line Tests

Run:

python test_local.py


Outputs include:

Generated secure code

Explanation

Diff

Token usage

Latency

Metrics stored to logs/metrics.csv

Recipes (RAG Guidelines)

The recipes/ folder contains remediation advice for:

SQL Injection (CWE-89)

XSS

Hardcoded secrets

SSRF

JWT validation issues

The RAG engine:

Embeds all recipe files

Computes similarity with the incoming request

Retrieves the most relevant guideline

Injects it into the prompt to improve quality

Performance Notes

First request triggers model warm-up (slow)

CPU inference takes ~40–60 seconds on DeepSeek 1.3B

Subsequent requests are faster

RAG step adds negligible overhead (<100 ms)

Limitations

Some models may not perfectly follow strict markers

Larger models require more RAM

RAG quality depends on recipe content