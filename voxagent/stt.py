from __future__ import annotations

from functools import lru_cache

from faster_whisper import WhisperModel

from voxagent.config import Settings


@lru_cache(maxsize=1)
def _load_model(model_name: str, device: str, compute_type: str) -> WhisperModel:
    return WhisperModel(model_name, device=device, compute_type=compute_type)


class SpeechToTextService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def transcribe(self, audio_path: str) -> tuple[str, str]:
        model = _load_model(
            self.settings.whisper_model,
            self.settings.whisper_device,
            self.settings.whisper_compute_type,
        )
        segments, _ = model.transcribe(audio_path, beam_size=5, vad_filter=True)
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
        return transcript, f"faster-whisper:{self.settings.whisper_model}"
