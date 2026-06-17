from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TRACKER_FILE = DATA_DIR / "application_tracker.json"
QUEUE_FILE = DATA_DIR / "approval_queue.json"
AUDIT_FILE = DATA_DIR / "audit_log.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def audit(event_type: str, details: Dict[str, Any]) -> None:
    record = {
        "timestamp": utc_now(),
        "event_type": event_type,
        "details": details,
    }
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_tracker() -> List[Dict[str, Any]]:
    return _read_json(TRACKER_FILE, [])


def save_tracker(items: List[Dict[str, Any]]) -> None:
    _write_json(TRACKER_FILE, items)


def upsert_application(application: Dict[str, Any]) -> None:
    tracker = load_tracker()
    key = application.get("application_id")
    replaced = False
    for i, item in enumerate(tracker):
        if item.get("application_id") == key:
            tracker[i] = {**item, **application, "updated_at": utc_now()}
            replaced = True
            break
    if not replaced:
        application.setdefault("created_at", utc_now())
        application.setdefault("updated_at", utc_now())
        tracker.append(application)
    save_tracker(tracker)
    audit("tracker_upsert", {"application_id": key, "status": application.get("status")})


def load_queue() -> List[Dict[str, Any]]:
    return _read_json(QUEUE_FILE, [])


def save_queue(items: List[Dict[str, Any]]) -> None:
    _write_json(QUEUE_FILE, items)


def add_to_approval_queue(item: Dict[str, Any]) -> None:
    queue = load_queue()
    queue.append(item)
    save_queue(queue)
    audit("approval_queued", {"application_id": item.get("application_id"), "title": item.get("job", {}).get("title")})


def update_queue_decision(application_id: str, decision: str, reviewer_note: str = "") -> Dict[str, Any] | None:
    queue = load_queue()
    updated = None
    for item in queue:
        if item.get("application_id") == application_id:
            item["approval_decision"] = decision
            item["reviewer_note"] = reviewer_note
            item["reviewed_at"] = utc_now()
            updated = item
            break
    save_queue(queue)
    audit("approval_decision", {"application_id": application_id, "decision": decision})
    return updated


def load_audit_log(limit: int = 200) -> List[Dict[str, Any]]:
    if not AUDIT_FILE.exists():
        return []
    lines = AUDIT_FILE.read_text(encoding="utf-8").splitlines()
    records = []
    for line in lines[-limit:]:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records
