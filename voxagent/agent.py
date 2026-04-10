from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from time import perf_counter

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
        started = perf_counter()
        transcript, stt_backend = self.stt_service.transcribe(audio_path)
        stt_elapsed = perf_counter() - started
        if not transcript:
            return AgentResponse(
                transcript="",
                intents=[],
                action_plan=[],
                action_results=[],
                llm_backend=self.llm_client.backend_name,
                stt_backend=stt_backend,
                notes=["No transcript could be extracted from the provided audio."],
                timings={"transcription_seconds": round(stt_elapsed, 3)},
            )

        plan_started = perf_counter()
        try:
            planned = self.llm_client.plan_actions(transcript)
            action_plan = [ActionRequest(**action.model_dump()) for action in planned.actions]
            intents = [action.intent for action in action_plan]
            notes = planned.notes
            requires_confirmation = planned.requires_confirmation or any(
                intent in {"create_file", "write_code"} for intent in intents
            )
            llm_backend = self.llm_client.backend_name
        except (requests.RequestException, ValueError) as error:
            action_plan, intents, notes, requires_confirmation = self.fallback_planner.plan(transcript)
            notes.append(f"Planner fallback reason: {type(error).__name__}")
            llm_backend = "rule-based-fallback"
        planning_elapsed = perf_counter() - plan_started

        action_results = []
        executor = ToolExecutor(self.settings, self.llm_client)
        file_operation_requested = any(
            action.intent in {"create_file", "write_code"} for action in action_plan
        )

        execution_started = perf_counter()
        if file_operation_requested and not approve_file_actions:
            notes.append("Execution paused until the UI confirmation checkbox is enabled.")
        else:
            for action in action_plan:
                action_results.append(executor.execute(action))
        execution_elapsed = perf_counter() - execution_started

        response = AgentResponse(
            transcript=transcript,
            intents=intents,
            action_plan=action_plan,
            action_results=action_results,
            llm_backend=llm_backend,
            stt_backend=stt_backend,
            requires_confirmation=requires_confirmation,
            notes=notes,
            timings={
                "transcription_seconds": round(stt_elapsed, 3),
                "planning_seconds": round(planning_elapsed, 3),
                "execution_seconds": round(execution_elapsed, 3),
            },
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
