from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionRequest:
    intent: str
    target_file: str | None = None
    target_folder: str | None = None
    language: str | None = None
    instruction: str | None = None
    text_to_summarize: str | None = None
    chat_response_hint: str | None = None


@dataclass
class ActionResult:
    intent: str
    status: str
    message: str
    output: str | None = None
    path: str | None = None


@dataclass
class AgentResponse:
    transcript: str
    intents: list[str]
    action_plan: list[ActionRequest]
    action_results: list[ActionResult]
    llm_backend: str
    stt_backend: str
    requires_confirmation: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass
class HistoryEntry:
    timestamp: str
    transcript: str
    intents: list[str]
    summary: str
    metadata: dict[str, Any] = field(default_factory=dict)
