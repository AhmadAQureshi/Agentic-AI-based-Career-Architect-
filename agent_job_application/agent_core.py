from __future__ import annotations

import hashlib
import re
from typing import Dict, List, Tuple

from drafting import grounded_draft
from privacy import kill_switch_is_on, privacy_scan_text
from storage import add_to_approval_queue, audit, upsert_application, utc_now


def _tokens(text: str) -> set[str]:
    return set(t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", text))


def score_job(profile_text: str, job: Dict[str, str]) -> Dict[str, object]:
    profile_tokens = _tokens(profile_text)
    job_tokens = _tokens(" ".join([
        job.get("title", ""),
        job.get("description", ""),
        job.get("location", ""),
        job.get("company", ""),
    ]))

    important = {
        "python", "sql", "power", "bi", "dashboard", "automation", "project", "management",
        "business", "analysis", "procurement", "vendor", "stakeholder", "reporting", "data",
        "ai", "luxembourg", "finance", "operations", "sap", "ariba", "pmp", "scrum"
    }

    overlap = profile_tokens & job_tokens
    weighted_hits = overlap & important

    base_score = min(60, len(overlap) * 3)
    weighted_bonus = min(35, len(weighted_hits) * 7)

    title_bonus = 0
    title_lower = job.get("title", "").lower()
    for phrase in ["business analyst", "project", "procurement", "data", "ai", "intern", "coordinator"]:
        if phrase in title_lower:
            title_bonus += 5

    score = min(100, base_score + weighted_bonus + min(title_bonus, 15))

    return {
        "score": int(score),
        "matched_keywords": sorted(list(overlap))[:30],
        "weighted_hits": sorted(list(weighted_hits)),
        "recommendation": "queue_for_review" if score >= 80 else "do_not_queue"
    }


def application_id(job: Dict[str, str]) -> str:
    key = "|".join([job.get("company", ""), job.get("title", ""), job.get("url", "")])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def evaluate_and_queue(profile_text: str, job: Dict[str, str], threshold: int = 80) -> Dict[str, object]:
    if kill_switch_is_on():
        audit("agent_blocked", {"reason": "kill_switch_on"})
        return {"blocked": True, "reason": "Kill switch is ON. No agent action was taken."}

    privacy_result = privacy_scan_text(profile_text)
    if not privacy_result["passed"]:
        audit("privacy_warning", {"hits": privacy_result["hits"]})

    result = score_job(profile_text, job)
    app_id = application_id(job)

    record = {
        "application_id": app_id,
        "job": job,
        "match_score": result["score"],
        "matched_keywords": result["matched_keywords"],
        "weighted_hits": result["weighted_hits"],
        "status": "below_threshold",
        "updated_at": utc_now()
    }

    if result["score"] >= threshold:
        draft = grounded_draft(job, profile_text)
        record.update({
            "status": "queued_for_human_approval",
            "draft": draft,
            "human_approval_required": True,
            "auto_submitted": False
        })
        add_to_approval_queue(record)
    else:
        audit("job_below_threshold", {"application_id": app_id, "score": result["score"], "threshold": threshold})

    upsert_application(record)
    return record
