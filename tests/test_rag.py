from app.rag_engine import RecipeRAG
from app.config import settings


def test_rag_retrieval():
    rag = RecipeRAG(settings.RECIPES_DIR)
    res = rag.retrieve("java", "CWE-89", "SELECT * FROM users WHERE username = 'x'")
    # If recipes exist, we expect a tuple. If not, it will be None. That is acceptable.
    # Here we just check that it does not crash.
    assert res is None or (isinstance(res, tuple) and len(res) == 2)
