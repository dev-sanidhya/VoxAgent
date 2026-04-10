from __future__ import annotations

from pathlib import Path

import requests

from voxagent.config import Settings
from voxagent.fallback import LocalFallbackResponder
from voxagent.models import ActionRequest, ActionResult
from voxagent.utils import ensure_output_path


class ToolExecutor:
    def __init__(self, settings: Settings, llm_client) -> None:
        self.settings = settings
        self.llm_client = llm_client
        self.fallback = LocalFallbackResponder()

    def execute(self, action: ActionRequest) -> ActionResult:
        if action.intent == "create_file":
            return self._create_file(action)
        if action.intent == "write_code":
            return self._write_code(action)
        if action.intent == "summarize_text":
            return self._summarize(action)
        if action.intent == "general_chat":
            return self._chat(action)
        return ActionResult(
            intent=action.intent,
            status="skipped",
            message=f"Unsupported intent: {action.intent}",
        )

    def _create_file(self, action: ActionRequest) -> ActionResult:
        if action.target_folder:
            target_folder = ensure_output_path(self.settings.output_dir, action.target_folder)
            target_folder.mkdir(parents=True, exist_ok=True)
            return ActionResult(
                intent=action.intent,
                status="success",
                message=f"Created folder {target_folder.name} in output/.",
                path=str(target_folder),
                backend="filesystem",
            )

        file_name = action.target_file or "new_file.txt"
        target_path = ensure_output_path(self.settings.output_dir, file_name)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.touch(exist_ok=True)
        return ActionResult(
            intent=action.intent,
            status="success",
            message=f"Created file {target_path.name} in output/.",
            path=str(target_path),
            backend="filesystem",
        )

    def _write_code(self, action: ActionRequest) -> ActionResult:
        file_name = action.target_file or "generated_code.py"
        instruction = action.instruction or "Create a starter file."
        target_path = ensure_output_path(self.settings.output_dir, file_name)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        backend = "ollama"
        try:
            code = self.llm_client.generate_code(
                instruction=instruction,
                language=action.language or "python",
                file_name=target_path.name,
            )
        except requests.RequestException:
            code = self.fallback.generate_code(
                instruction=instruction,
                language=action.language or "python",
                file_name=target_path.name,
            )
            backend = "local-fallback"
        target_path.write_text(code.rstrip() + "\n", encoding="utf-8")
        return ActionResult(
            intent=action.intent,
            status="success",
            message=f"Wrote generated {action.language or 'code'} to {target_path.name}.",
            output=code,
            path=str(target_path),
            backend=backend,
        )

    def _summarize(self, action: ActionRequest) -> ActionResult:
        text = action.text_to_summarize or action.instruction or ""
        if not text.strip():
            return ActionResult(
                intent=action.intent,
                status="failed",
                message="No text was provided to summarize.",
                backend="local-validation",
            )
        backend = "ollama"
        try:
            summary = self.llm_client.summarize(text)
        except requests.RequestException:
            summary = self.fallback.summarize(text)
            backend = "local-fallback"
        return ActionResult(
            intent=action.intent,
            status="success",
            message="Created a text summary.",
            output=summary,
            backend=backend,
        )

    def _chat(self, action: ActionRequest) -> ActionResult:
        prompt = action.instruction or action.chat_response_hint or "Respond to the user."
        backend = "ollama"
        try:
            response = self.llm_client.chat(prompt)
        except requests.RequestException:
            response = self.fallback.chat(prompt)
            backend = "local-fallback"
        return ActionResult(
            intent=action.intent,
            status="success",
            message="Generated a chat response.",
            output=response,
            backend=backend,
        )


class FallbackToolExecutor:
    """Used only for isolated utility access in environments without Ollama."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create_empty_file(self, file_name: str) -> Path:
        target_path = ensure_output_path(self.settings.output_dir, file_name)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.touch(exist_ok=True)
        return target_path
