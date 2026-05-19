import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    telegram_token: str | None = os.getenv("TELEGRAM_TOKEN")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    num_papers: int = _int_env("NUM_PAPERS", 5)
    arxiv_results_per_query: int = _int_env("ARXIV_RESULTS_PER_QUERY", 4)
    arxiv_delay_seconds: float = _float_env("ARXIV_DELAY_SECONDS", 3.0)
    arxiv_retries: int = _int_env("ARXIV_RETRIES", 3)
    extraction_max_chars: int = _int_env("EXTRACTION_MAX_CHARS", 4500)
    telegram_message_limit: int = _int_env("TELEGRAM_MESSAGE_LIMIT", 3900)
    request_timeout_seconds: int = _int_env("REQUEST_TIMEOUT_SECONDS", 30)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def validate_for_bot(self) -> None:
        missing = []
        if not self.telegram_token:
            missing.append("TELEGRAM_TOKEN")
        if not self.groq_api_key:
            missing.append("GROQ_API_KEY")
        if missing:
            names = ", ".join(missing)
            raise RuntimeError(f"Missing required environment variable(s): {names}")


settings = Settings()

# Backwards-compatible constants for existing imports.
NUM_PAPERS = settings.num_papers
GROQ_MODEL = settings.groq_model
