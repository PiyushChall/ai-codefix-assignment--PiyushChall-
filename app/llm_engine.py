import re
import time
from typing import Optional, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from .config import settings
from .logging_utils import logger


PROMPT_TEMPLATE = """
You MUST output EXACTLY AND ONLY the following format.

<<<FIXED_CODE>>>
<secure code only, no explanation, no backticks>
<<<END_FIXED_CODE>>>

<<<EXPLANATION>>>
<clear explanation only, no code blocks, no backticks>
<<<END_EXPLANATION>>>

DO NOT output anything else outside these markers.
DO NOT wrap code in ``` fencing.
DO NOT repeat the prompt.
DO NOT invent any additional sections.

Now fix this code:

Language: {language}
CWE: {cwe}

Guidelines:
{guidelines}

<<<VULNERABLE_CODE>>>
{code}
<<<END_VULNERABLE_CODE>>>
"""


class LocalLLM:
    def __init__(self):
        logger.info(f"Loading model {settings.MODEL_NAME} on {settings.DEVICE}")
        self.tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            settings.MODEL_NAME,
            trust_remote_code=True,
            torch_dtype=torch.float16 if settings.DEVICE == "cuda" else torch.float32
        )
        self.model.to(settings.DEVICE)
        self.model.eval()
        self.model_name = settings.MODEL_NAME

    def generate_fix(
        self,
        language: str,
        cwe: str,
        code: str,
        guidelines: Optional[str] = None,
    ) -> Tuple[str, str, int, int, int]:
        """
        Returns:
            fixed_code, explanation, input_tokens, output_tokens, latency_ms
        """
        prompt = PROMPT_TEMPLATE.format(
            language=language,
            cwe=cwe,
            guidelines=guidelines or "",
            code=code,
        )

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
        input_ids = input_ids.to(self.model.device)

        input_tokens = input_ids.shape[1]

        start = time.perf_counter()
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_new_tokens=settings.MAX_NEW_TOKENS,
                temperature=settings.TEMPERATURE,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        end = time.perf_counter()

        latency_ms = int((end - start) * 1000)

        # Drop the prompt part
        generated_ids = output_ids[0, input_ids.shape[1]:]
        output_tokens = int(generated_ids.shape[0])

        output_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        fixed_code = self._extract_between_markers(output_text, "FIXED_CODE")
        explanation = self._extract_between_markers(output_text, "EXPLANATION")

        if not fixed_code:
            logger.warning("Failed to parse FIXED_CODE from model output")
            fixed_code = "// Parsing error. Model output:\n" + output_text

        if not explanation:
            explanation = "No structured explanation was parsed from the model output."

        return fixed_code.strip(), explanation.strip(), input_tokens, output_tokens, latency_ms

    @staticmethod
    def _extract_between_markers(text: str, marker: str) -> str:
        pattern = rf"<<<{marker}>>>(.*?)<<<END_{marker}>>>"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
        return ""
