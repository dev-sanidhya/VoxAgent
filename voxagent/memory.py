from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from voxagent.models import HistoryEntry


class HistoryStore:
    def __init__(self, history_file: str) -> None:
        self.history_file = history_file

    def load(self) -> list[dict[str, Any]]:
        try:
            with open(self.history_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, list):
                return data
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
        return []

    def append(self, entry: HistoryEntry) -> None:
        history = self.load()
        history.append(asdict(entry))
        with open(self.history_file, "w", encoding="utf-8") as handle:
            json.dump(history[-25:], handle, indent=2)
