from pathlib import Path

class Settings:
    MODEL_NAME: str = "deepseek-ai/deepseek-coder-1.3b-instruct"
    DEVICE: str = "cpu"  # or "cuda" if available
    MAX_NEW_TOKENS: int = 512
    TEMPERATURE: float = 0.2
    RECIPES_DIR: Path = Path(__file__).resolve().parent.parent / "recipes"
    LOG_DIR: Path = Path(__file__).resolve().parent.parent / "logs"

settings = Settings()
settings.LOG_DIR.mkdir(exist_ok=True)
