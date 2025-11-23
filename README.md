# QodeFix. AI Code Remediation Microservice

Local LLM. FastAPI. Secure Code Fixing. Optional RAG.

QodeFix is an AI powered code remediation microservice. It accepts insecure code and returns a secure corrected version, a unified diff, a clear explanation of the vulnerability, and inference metrics. It runs entirely on local inference using DeepSeek Coder 1.3B or any Hugging Face model and supports CPU only. An optional RAG layer powered by FAISS and SentenceTransformers improves the consistency and accuracy of generated fixes.

---

## System Flow Diagram

![Flow Diagram](qodefixer.drawio (1).png)

Refer to the included file `qodefixer.drawio (1).png` for the original diagram.

---

## Features

### 1. Local LLM Inference
- Runs using the Transformers library
- Works with DeepSeek Coder or any local Hugging Face model
- CPU only, no GPU required
- No external paid APIs
- Uses structured prompts for consistent and stable output

### 2. FastAPI Microservice
- Exposes a single endpoint: `POST /local_fix`
- Uses Pydantic for request and response validation

### 3. Security Focused Prompt Engineering

The service enforces strict output markers.  
They are wrapped inside fenced code blocks to prevent misinterpretation by Markdown.

<<<FIXED_CODE>>>
... fixed code output ...
<<<END_FIXED_CODE>>>

<<<EXPLANATION>>>
... explanation output ...
<<<END_EXPLANATION>>>


### 4. Unified Diff Generation
- Generates a clean unified diff using Python difflib
- Highlights all modifications introduced during remediation

### 5. Logging and Metrics
- Tracks token usage
- Measures inference latency in milliseconds
- Records the model used
- Metrics are saved into `logs/metrics.csv`

### 6. Mini RAG. Retrieval Augmented Generation
- FAISS based vector similarity search
- Embeds remediation guidelines from the `recipes/` directory
- Picks the most relevant guideline based on CWE and code context
- Injects the selected guideline into the LLM prompt for improved accuracy

---

## Installation

### 1. Create and Activate Virtual Environment

python -m venv .venv
.\.venv\Scripts\activate   # Windows

### 2. Install Dependencies

pip install -r requirements.txt

### 3. Model Download

Transformers downloads DeepSeek Coder automatically during first execution.
Approximate model size: 2.7 GB.

---

## Running the Service

### Start the FastAPI server:

uvicorn app.main:app --reload

### API Documentation

Open the Swagger UI:
http://127.0.0.1:8000/docs

Use the Try it out button on the /local_fix endpoint.

### Example Request
{
  "language": "java",
  "cwe": "CWE-89",
  "code": "String query = \"SELECT * FROM users WHERE username = '\" + userInput + \"'\";"
}

### Command Line Testing

Run the test script:
python test_local.py

The output will include:
Secure fixed code
Explanation of the vulnerability
Unified diff
Token usage statistics
Inference latency
Log entry written to logs/metrics.csv

---

## Recipes for RAG

The recipes/ directory contains rule based guidelines for issues such as:
SQL Injection. CWE 89
XSS
Hardcoded secrets
SSRF
JWT validation issues

### RAG Process

Embed all recipe files
Compute similarity with the incoming request
Select the most relevant guideline
Provide it to the prompt before LLM generation
This step usually adds less than 100 milliseconds to processing time.

---

## Performance Notes

The first request triggers model warm up and is slower
CPU inference with DeepSeek Coder 1.3B usually takes 40 to 60 seconds
Following requests are significantly faster
The RAG step adds minimal overhead

---

## Limitations

Some models may not follow the strict output markers perfectly
Larger models require more RAM
RAG precision depends on the quality of recipes provided
