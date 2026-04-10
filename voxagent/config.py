from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    output_dir: Path
    history_dir: Path
    history_file: Path
    whisper_model: str
    whisper_device: str
    whisper_compute_type: str
    ollama_base_url: str
    ollama_model: str
    planner_timeout_seconds: int
    generation_timeout_seconds: int


def get_settings() -> Settings:
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "output"
    history_dir = repo_root / "history"
    output_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)
    history_file = history_dir / "session_history.json"

    return Settings(
        repo_root=repo_root,
        output_dir=output_dir,
        history_dir=history_dir,
        history_file=history_file,
        whisper_model=os.getenv("WHISPER_MODEL", "base.en"),
        whisper_device=os.getenv("WHISPER_DEVICE", "cpu"),
        whisper_compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        planner_timeout_seconds=int(os.getenv("PLANNER_TIMEOUT_SECONDS", "20")),
        generation_timeout_seconds=int(os.getenv("GENERATION_TIMEOUT_SECONDS", "45")),
    )
