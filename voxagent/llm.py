from __future__ import annotations

import json
from typing import Any

import requests
from pydantic import BaseModel, Field, ValidationError

from voxagent.config import Settings


class PlannedAction(BaseModel):
    intent: str
    target_file: str | None = None
    target_folder: str | None = None
    language: str | None = None
    instruction: str | None = None
    text_to_summarize: str | None = None
    chat_response_hint: str | None = None


class AgentPlan(BaseModel):
    requires_confirmation: bool = False
    notes: list[str] = Field(default_factory=list)
    actions: list[PlannedAction]


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def backend_name(self) -> str:
        return f"ollama:{self.settings.ollama_model}"

    def _chat_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.settings.ollama_base_url}/api/chat",
            json={
                "model": self.settings.ollama_model,
                "format": "json",
                "stream": False,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["message"]["content"]
        return json.loads(content)

    def _chat_text(self, system_prompt: str, user_prompt: str) -> str:
        response = requests.post(
            f"{self.settings.ollama_base_url}/api/chat",
            json={
                "model": self.settings.ollama_model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["message"]["content"].strip()

    def plan_actions(self, transcript: str) -> AgentPlan:
        system_prompt = (
            "You are an intent router for a local voice agent. "
            "Return strict JSON with keys requires_confirmation, notes, and actions. "
            "Each action must use one intent from: create_file, write_code, summarize_text, general_chat. "
            "Use multiple actions if the request is compound. "
            "Any file path must be just a simple file name, not an absolute path. "
            "If the user wants a folder, use intent create_file and fill target_folder. "
            "For summarize_text, include text_to_summarize with the text to summarize. "
            "For general_chat, include chat_response_hint. "
            "For write_code, include target_file, language, and instruction."
        )
        raw_plan = self._chat_json(system_prompt, transcript)
        try:
            return AgentPlan.model_validate(raw_plan)
        except ValidationError as error:
            raise ValueError(f"Invalid planner response: {error}") from error

    def generate_code(self, instruction: str, language: str, file_name: str) -> str:
        system_prompt = (
            "You write clean production-ready code. "
            "Return code only. No markdown fences. "
            "Match the requested language and keep the output focused."
        )
        user_prompt = (
            f"Create {language or 'code'} for file {file_name}. "
            f"User instruction: {instruction}"
        )
        return self._chat_text(system_prompt, user_prompt)

    def summarize(self, text: str) -> str:
        system_prompt = (
            "Summarize the user's text clearly and concisely. "
            "Preserve key facts and actions. Keep the answer under 120 words unless the text is very long."
        )
        return self._chat_text(system_prompt, text)

    def chat(self, transcript: str) -> str:
        system_prompt = (
            "You are a helpful local desktop AI assistant. "
            "Answer clearly and directly."
        )
        return self._chat_text(system_prompt, transcript)
