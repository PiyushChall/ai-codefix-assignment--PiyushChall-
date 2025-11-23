import difflib
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import CodeFixRequest, CodeFixResponse, TokenUsage
from .llm_engine import LocalLLM
from .rag_engine import RecipeRAG
from .logging_utils import logger, log_metrics
from .config import settings

app = FastAPI(
    title="AI Code Remediation Microservice",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global singletons
llm = LocalLLM()
rag = RecipeRAG(settings.RECIPES_DIR)


def compute_diff(original: str, fixed: str) -> str:
    diff_lines = difflib.unified_diff(
        original.splitlines(),
        fixed.splitlines(),
        fromfile="vulnerable",
        tofile="fixed",
        lineterm=""
    )
    return "\n".join(diff_lines)


@app.post("/local_fix", response_model=CodeFixResponse)
async def local_fix(body: CodeFixRequest) -> CodeFixResponse:
    language = body.language
    cwe = body.cwe
    code = body.code

    # RAG retrieval
    rag_guidelines = None
    rag_name = None
    rag_result = rag.retrieve(language, cwe, code)
    if rag_result:
        rag_guidelines, rag_name = rag_result

    logger.info(
        f"Received /local_fix request. language={language}, cwe={cwe}, "
        f"rag_recipe={rag_name}"
    )

    # LLM inference
    fixed_code, explanation, input_tokens, output_tokens, model_latency_ms = llm.generate_fix(
        language=language,
        cwe=cwe,
        code=code,
        guidelines=rag_guidelines,
    )

    # Diff
    diff_text = compute_diff(code, fixed_code)

    # For API we want end to end latency. Here for simplicity we reuse the LLM latency.
    latency_ms = model_latency_ms

    # Metrics
    metrics_row = {
        "language": language,
        "cwe": cwe,
        "model_used": llm.model_name,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
    }
    log_metrics(metrics_row)

    return CodeFixResponse(
        fixed_code=fixed_code,
        diff=diff_text,
        explanation=explanation,
        model_used=llm.model_name,
        token_usage=TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        ),
        latency_ms=latency_ms,
    )
