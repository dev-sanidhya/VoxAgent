from __future__ import annotations

import re

from voxagent.models import ActionRequest


class LocalFallbackPlanner:
    SPOKEN_EXTENSIONS = {
        " dot py": ".py",
        " dot txt": ".txt",
        " dot md": ".md",
        " dot json": ".json",
        " dot js": ".js",
        " dot ts": ".ts",
        " dot html": ".html",
        " dot css": ".css",
    }

    @classmethod
    def _normalize_spoken_extensions(cls, transcript: str) -> str:
        normalized = transcript
        for spoken, ext in cls.SPOKEN_EXTENSIONS.items():
            normalized = re.sub(spoken, ext, normalized, flags=re.IGNORECASE)
        return normalized

    @staticmethod
    def _extract_file_name(transcript: str, default_name: str) -> str:
        match = re.search(r"([A-Za-z0-9_-]+\.[A-Za-z0-9]+)", transcript)
        return match.group(1) if match else default_name

    @staticmethod
    def _extract_folder_name(transcript: str) -> str | None:
        match = re.search(r"folder(?: named)? ([A-Za-z0-9_-]+)", transcript, re.IGNORECASE)
        return match.group(1) if match else None

    def plan(self, transcript: str) -> tuple[list[ActionRequest], list[str], list[str], bool]:
        transcript = self._normalize_spoken_extensions(transcript)
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


class LocalFallbackResponder:
    def summarize(self, text: str) -> str:
        compact = " ".join(text.split())
        if len(compact) <= 140:
            return compact
        parts = re.split(r"(?<=[.!?])\s+", compact)
        if len(parts) >= 2:
            return " ".join(parts[:2]).strip()
        return compact[:140].rstrip() + "..."

    def chat(self, prompt: str) -> str:
        return (
            "I am running in offline fallback mode, so this response is rule-based. "
            f"You said: {prompt}"
        )

    def generate_code(self, instruction: str, language: str, file_name: str) -> str:
        language_key = (language or "").lower()
        if "python" in language_key or file_name.endswith(".py"):
            return (
                '"""Generated in fallback mode because the local LLM was unavailable."""\n\n'
                "import time\n\n\n"
                "def retry(operation, attempts=3, delay_seconds=1):\n"
                "    last_error = None\n"
                "    for _ in range(attempts):\n"
                "        try:\n"
                "            return operation()\n"
                "        except Exception as error:\n"
                "            last_error = error\n"
                "            time.sleep(delay_seconds)\n"
                "    raise last_error\n"
            )

        return (
            f"// Generated in fallback mode because the local LLM was unavailable.\n"
            f"// Original instruction: {instruction}\n"
        )
