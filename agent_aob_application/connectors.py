from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Protocol

from storage import audit


@dataclass
class JobPosting:
    source: str
    company: str
    title: str
    location: str
    url: str
    description: str
    posted_date: str = ""


class JobConnector(Protocol):
    name: str

    def fetch(self) -> List[JobPosting]:
        ...


class SampleJsonConnector:
    """Demo connector. Replace with real source connectors after ToS approval."""

    name = "sample_json_connector"

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def fetch(self) -> List[JobPosting]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        jobs = [JobPosting(**item) for item in raw]
        audit("connector_fetch", {"connector": self.name, "count": len(jobs)})
        return jobs


class LinkedInAlertConnector:
    """
    Safer LinkedIn approach:
    - Use user-owned LinkedIn job alerts delivered to email, or a manual export.
    - Do not scrape LinkedIn pages unless a current ToS/legal review explicitly allows it.
    """

    name = "linkedin_alert_connector"

    def fetch(self) -> List[JobPosting]:
        audit("connector_skipped", {
            "connector": self.name,
            "reason": "requires email integration and ToS-approved workflow"
        })
        return []


class CompanyCareerPageConnector:
    """
    Placeholder for company career pages.
    Production implementation should prefer:
    - official public jobs API,
    - RSS/sitemap if provided,
    - low-frequency HTTP access only after ToS/robots/legal review.
    """

    name = "company_career_page_connector"

    def fetch(self) -> List[JobPosting]:
        audit("connector_skipped", {
            "connector": self.name,
            "reason": "requires per-site ToS review before automated access"
        })
        return []


class JobBoardApiConnector:
    """Placeholder for official job board APIs."""

    name = "job_board_api_connector"

    def fetch(self) -> List[JobPosting]:
        audit("connector_skipped", {
            "connector": self.name,
            "reason": "requires API key and API terms approval"
        })
        return []


def jobs_to_dicts(jobs: Iterable[JobPosting]) -> List[Dict[str, str]]:
    return [asdict(job) for job in jobs]
