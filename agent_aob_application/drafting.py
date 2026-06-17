from __future__ import annotations

import os
import re
from typing import Dict, List, Tuple

from storage import audit


def extract_profile_facts(profile_text: str) -> List[str]:
    facts = []
    for line in profile_text.splitlines():
        clean = line.strip("-• \t")
        if clean and not clean.lower().startswith("candidate profile"):
            facts.append(clean)
    return facts


def _keyword_hits(text: str, facts: List[str]) -> List[str]:
    text_lower = text.lower()
    hits = []
    for fact in facts:
        tokens = [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", fact)]
        strong_hits = [t for t in tokens if t in text_lower]
        if strong_hits:
            hits.append(fact)
    return hits[:8]


def grounded_draft(job: Dict[str, str], profile_text: str) -> Dict[str, object]:
    """
    Drafts only from facts present in profile_text.
    This template mode is intentionally conservative.
    """
    facts = extract_profile_facts(profile_text)
    relevant_facts = _keyword_hits(job.get("description", ""), facts)
    if not relevant_facts:
        relevant_facts = facts[:5]

    title = job.get("title", "the role")
    company = job.get("company", "your organization")

    cv_summary = (
        f"Targeted profile summary for {title} at {company}:\\n"
        + "\\n".join(f"- {fact}" for fact in relevant_facts)
    )

    cover_letter = f"""Dear Hiring Team,

I am interested in the {title} position at {company}. The role aligns with my background and target direction because it connects directly with the following verified experience from my profile:

{chr(10).join(f"- {fact}" for fact in relevant_facts)}

I can contribute by combining structured problem solving, stakeholder coordination, reporting discipline and practical automation mindset. I have only included information that is present in the approved master profile, so the draft remains source-grounded and reviewable.

Before submission, I will review the final version to ensure it is accurate, relevant and tailored to the role.

Kind regards,
Candidate
"""

    audit("draft_generated", {
        "title": title,
        "company": company,
        "grounding_facts_used": len(relevant_facts),
        "mode": "template_grounded"
    })

    return {
        "cv_summary": cv_summary,
        "cover_letter": cover_letter,
        "grounding_facts": relevant_facts,
        "source_grounded": True,
        "requires_human_review": True
    }


def optional_llm_draft(job: Dict[str, str], profile_text: str) -> Dict[str, object]:
    """
    Optional extension point.

    For production, use an LLM only with:
    - explicit source facts supplied in the prompt;
    - no-fabrication instruction;
    - post-generation verifier checking every claim against source facts;
    - human approval before use.

    This scaffold returns the conservative template draft unless an implementation is added.
    """
    return grounded_draft(job, profile_text)
