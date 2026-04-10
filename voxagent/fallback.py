from __future__ import annotations

import re

from voxagent.models import ActionRequest


class LocalFallbackPlanner:
    @staticmethod
    def _extract_file_name(transcript: str, default_name: str) -> str:
        match = re.search(r"([A-Za-z0-9_-]+\.[A-Za-z0-9]+)", transcript)
        return match.group(1) if match else default_name

    @staticmethod
    def _extract_folder_name(transcript: str) -> str | None:
        match = re.search(r"folder(?: named)? ([A-Za-z0-9_-]+)", transcript, re.IGNORECASE)
        return match.group(1) if match else None

    def plan(self, transcript: str) -> tuple[list[ActionRequest], list[str], list[str], bool]:
        lowered = transcript.lower()
        notes = ["Fell back to rule-based intent parsing because Ollama was unavailable."]
        actions: list[ActionRequest] = []
        target_file = self._extract_file_name(transcript, "generated_code.py")
        target_folder = self._extract_folder_name(transcript)

        if "summarize" in lowered:
            text = transcript.split("summarize", 1)[-1].strip(" :,-")
            actions.append(
                ActionRequest(
                    intent="summarize_text",
                    text_to_summarize=text,
                    instruction=text,
                )
            )
        if "create" in lowered and "folder" in lowered:
            actions.append(ActionRequest(intent="create_file", target_folder=target_folder or "new_folder"))
        if "create" in lowered and "file" in lowered and not any(a.intent == "write_code" for a in actions):
            actions.append(ActionRequest(intent="create_file", target_file=target_file))
        if any(keyword in lowered for keyword in ["code", "python", "function", "script"]):
            actions.append(
                ActionRequest(
                    intent="write_code",
                    target_file=target_file,
                    language="python",
                    instruction=transcript,
                )
            )
        if not actions:
            actions.append(
                ActionRequest(
                    intent="general_chat",
                    instruction=transcript,
                    chat_response_hint=transcript,
                )
            )

        intents = [action.intent for action in actions]
        return actions, intents, notes, any(intent in {"create_file", "write_code"} for intent in intents)
