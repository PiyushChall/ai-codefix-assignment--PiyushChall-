from pathlib import Path
from typing import Optional, Tuple, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .config import settings
from .logging_utils import logger


class RecipeRAG:
    def __init__(self, recipes_dir: Path):
        self.recipes_dir = recipes_dir
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.index = None
        self.recipe_texts: List[str] = []
        self.recipe_names: List[str] = []
        self._build_index()

    def _build_index(self) -> None:
        if not self.recipes_dir.exists():
            logger.warning(f"Recipes directory {self.recipes_dir} does not exist")
            return

        texts = []
        names = []

        for path in sorted(self.recipes_dir.glob("*.txt")):
            content = path.read_text(encoding="utf-8")
            texts.append(content)
            names.append(path.name)

        if not texts:
            logger.warning("No recipe files found for RAG")
            return

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)

        self.index = index
        self.recipe_texts = texts
        self.recipe_names = names
        logger.info(f"RAG index built with {len(texts)} recipes")

    def retrieve(self, language: str, cwe: str, code: str) -> Optional[Tuple[str, str]]:
        """Return (recipe_text, recipe_name) for top1 match."""
        if self.index is None:
            return None

        query = f"Language: {language}\nCWE: {cwe}\nCode:\n{code}"
        q_emb = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(q_emb, 1)
        idx = int(indices[0][0])
        return self.recipe_texts[idx], self.recipe_names[idx]
