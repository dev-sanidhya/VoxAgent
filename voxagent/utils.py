from __future__ import annotations

import re
import tempfile
from pathlib import Path


def slugify_filename(raw_value: str, default_name: str = "generated.txt") -> str:
    cleaned = raw_value.strip().replace("\\", "/").split("/")[-1]
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", cleaned).strip("._")
    return cleaned or default_name


def ensure_output_path(output_dir: Path, file_name: str) -> Path:
    if any(token in file_name for token in ("..", "/", "\\")):
        raise ValueError("Only simple file or folder names are allowed inside output/.")
    safe_name = slugify_filename(file_name)
    target = (output_dir / safe_name).resolve()
    if output_dir.resolve() not in target.parents and target != output_dir.resolve():
        raise ValueError("Target path escaped the output directory.")
    return target


def write_temp_audio(audio_bytes: bytes, suffix: str = ".wav") -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(audio_bytes)
        return handle.name
