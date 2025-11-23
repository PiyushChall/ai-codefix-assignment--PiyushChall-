from pydantic import BaseModel, Field

class TokenUsage(BaseModel):
    input_tokens: int = Field(..., ge=0)
    output_tokens: int = Field(..., ge=0)

class CodeFixRequest(BaseModel):
    language: str = Field(..., example="java")
    cwe: str = Field(..., example="CWE-89")
    code: str = Field(..., example="<vulnerable snippet>")

class CodeFixResponse(BaseModel):
    fixed_code: str
    diff: str
    explanation: str
    model_used: str
    token_usage: TokenUsage
    latency_ms: int
