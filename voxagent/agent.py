from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone

import requests

from voxagent.config import Settings
from voxagent.fallback import LocalFallbackPlanner
from voxagent.llm import OllamaClient
from voxagent.memory import HistoryStore
from voxagent.models import ActionRequest, ActionResult, AgentResponse, HistoryEntry
from voxagent.stt import SpeechToTextService
from voxagent.tools import ToolExecutor

class VoiceAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.stt_service = SpeechToTextService(settings)
        self.history_store = HistoryStore(str(settings.history_file))
        self.llm_client = OllamaClient(settings)
        self.fallback_planner = LocalFallbackPlanner()

    def process_audio(self, audio_path: str, approve_file_actions: bool = False) -> AgentResponse:
        transcript, stt_backend = self.stt_service.transcribe(audio_path)
        if not transcript:
            return AgentResponse(
                transcript="",
                intents=[],
                action_plan=[],
                action_results=[],
                llm_backend=self.llm_client.backend_name,
                stt_backend=stt_backend,
                notes=["No transcript could be extracted from the provided audio."],
            )

        try:
            planned = self.llm_client.plan_actions(transcript)
            action_plan = [ActionRequest(**action.model_dump()) for action in planned.actions]
            intents = [action.intent for action in action_plan]
            notes = planned.notes
            requires_confirmation = planned.requires_confirmation or any(
                intent in {"create_file", "write_code"} for intent in intents
            )
            llm_backend = self.llm_client.backend_name
        except (requests.RequestException, ValueError):
            action_plan, intents, notes, requires_confirmation = self.fallback_planner.plan(transcript)
            llm_backend = "rule-based-fallback"

        action_results = []
        executor = ToolExecutor(self.settings, self.llm_client)
        file_operation_requested = any(
            action.intent in {"create_file", "write_code"} for action in action_plan
        )

        if file_operation_requested and not approve_file_actions:
            notes.append("Execution paused until the UI confirmation checkbox is enabled.")
        else:
            for action in action_plan:
                try:
                    action_results.append(executor.execute(action))
                except requests.RequestException as error:
                    action_results.append(
                        ActionResult(
                            intent="general_chat",
                            status="failed",
                            message=f"Tool execution failed because the LLM backend was unavailable: {error}",
                        )
                    )

        response = AgentResponse(
            transcript=transcript,
            intents=intents,
            action_plan=action_plan,
            action_results=action_results,
            llm_backend=llm_backend,
            stt_backend=stt_backend,
            requires_confirmation=requires_confirmation,
            notes=notes,
        )
        self._persist_history(response)
        return response

    def _persist_history(self, response: AgentResponse) -> None:
        preview = response.action_results[0].message if response.action_results else "Planned actions only"
        self.history_store.append(
            HistoryEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                transcript=response.transcript,
                intents=response.intents,
                summary=preview,
                metadata={
                    "stt_backend": response.stt_backend,
                    "llm_backend": response.llm_backend,
                    "notes": response.notes,
                    "actions": [asdict(action) for action in response.action_plan],
                },
            )
        )
