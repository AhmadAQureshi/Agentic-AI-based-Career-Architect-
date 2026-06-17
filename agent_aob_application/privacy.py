from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

SENSITIVE_HINTS = [
    "passport", "national id", "id card", "bank account", "password", "api key",
    "secret", "token", "medical", "religion", "political", "criminal"
]


def kill_switch_is_on() -> bool:
    env_value = os.getenv("KILL_SWITCH", "").strip().lower()
    file_switch = (Path(__file__).parent / "KILL_SWITCH_ON").exists()
    return env_value in {"1", "true", "yes", "on"} or file_switch


def privacy_scan_text(text: str) -> Dict[str, object]:
    lowered = text.lower()
    hits: List[str] = [hint for hint in SENSITIVE_HINTS if hint in lowered]
    return {
        "passed": len(hits) == 0,
        "hits": hits,
        "recommendation": "Remove unnecessary sensitive data before processing." if hits else "No obvious sensitive hints detected."
    }


def retention_policy_summary(retention_days: int = 180) -> str:
    return (
        f"Keep application logs for {retention_days} days unless the user requests deletion earlier. "
        "Do not store portal passwords. Keep API keys only in environment variables or a secret manager."
    )
