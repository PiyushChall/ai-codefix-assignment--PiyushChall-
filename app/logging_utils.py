import csv
import logging
from pathlib import Path
from typing import Dict, Any

from .config import settings

LOG_FILE = settings.LOG_DIR / "service.log"
METRICS_FILE = settings.LOG_DIR / "metrics.csv"

# Basic logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ],
)

logger = logging.getLogger("ai-codefix")

# Ensure metrics CSV header
if not METRICS_FILE.exists():
    with open(METRICS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["language", "cwe", "model_used",
                           "input_tokens", "output_tokens", "latency_ms"]
        )
        writer.writeheader()


def log_metrics(row: Dict[str, Any]) -> None:
    """Append one row of metrics to metrics.csv."""
    with open(METRICS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["language", "cwe", "model_used",
                           "input_tokens", "output_tokens", "latency_ms"]
        )
        writer.writerow(row)
    logger.info(f"Metrics: {row}")
