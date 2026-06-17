from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from agent_core import evaluate_and_queue
from connectors import SampleJsonConnector, jobs_to_dicts
from notifications import notify_user
from privacy import kill_switch_is_on, privacy_scan_text, retention_policy_summary
from storage import load_audit_log, load_queue, load_tracker, update_queue_decision, upsert_application

APP_DIR = Path(__file__).parent
SAMPLE_PROFILE = APP_DIR / "sample_profile.txt"
SAMPLE_JOBS = APP_DIR / "sample_jobs.json"
SAMPLE_SOURCES = APP_DIR / "sample_sources.json"

st.set_page_config(page_title="AI Job Search Agent", page_icon="🎯", layout="wide")

st.title("🎯 AI Job Search Agent — Real-Agent Scaffold")
st.caption("Automate the work. Never the truth. Never the decision.")

with st.sidebar:
    st.header("Control Panel")
    threshold = st.slider("Match threshold", min_value=50, max_value=95, value=80, step=5)
    notification_channel = st.selectbox("Notification mode", ["audit_only", "email"])
    st.warning("Kill switch is ON" if kill_switch_is_on() else "Kill switch is OFF")
    st.caption("Create a file named KILL_SWITCH_ON in this folder or set KILL_SWITCH=true to stop agent actions.")

tabs = st.tabs([
    "1. Profile",
    "2. Job sources",
    "3. Monitor & match",
    "4. Approval workflow",
    "5. Reports",
    "6. Governance"
])

with tabs[0]:
    st.subheader("Candidate profile")
    default_profile = SAMPLE_PROFILE.read_text(encoding="utf-8")
    profile_text = st.text_area("Master profile / source of truth", value=default_profile, height=350)
    scan = privacy_scan_text(profile_text)
    if scan["passed"]:
        st.success(scan["recommendation"])
    else:
        st.warning(f"{scan['recommendation']} Hits: {', '.join(scan['hits'])}")
    st.info("Drafts must be generated only from this approved profile. No fabricated experience allowed.")

with tabs[1]:
    st.subheader("Job source connectors")
    sources = json.loads(SAMPLE_SOURCES.read_text(encoding="utf-8"))
    st.dataframe(pd.DataFrame(sources), use_container_width=True)
    st.markdown("""
**Production connector rule**

Use official APIs, user-owned alerts, RSS/sitemaps, or approved exports.  
Do not scrape or auto-submit on portals until Terms-of-Service review is completed.
""")

with tabs[2]:
    st.subheader("Monitor selected sources and evaluate jobs")
    connector = SampleJsonConnector(SAMPLE_JOBS)
    jobs = jobs_to_dicts(connector.fetch())
    df_jobs = pd.DataFrame(jobs)
    st.dataframe(df_jobs[["company", "title", "location", "source", "posted_date"]], use_container_width=True)

    selected_idx = st.selectbox("Select job to evaluate", list(range(len(jobs))), format_func=lambda i: f"{jobs[i]['company']} — {jobs[i]['title']}")
    selected_job = jobs[selected_idx]
    with st.expander("View job description", expanded=True):
        st.write(selected_job["description"])
        st.caption(selected_job["url"])

    if st.button("Run agent: match, draft and queue if above threshold"):
        result = evaluate_and_queue(profile_text, selected_job, threshold=threshold)
        if result.get("blocked"):
            st.error(result["reason"])
        else:
            st.metric("Match score", f"{result['match_score']}%")
            st.write("Status:", result["status"])
            st.write("Weighted hits:", ", ".join(result.get("weighted_hits", [])) or "None")
            if result["status"] == "queued_for_human_approval":
                st.success("Queued for human approval. Nothing has been submitted.")
                notify_user(
                    "AI Job Search Agent: role queued for approval",
                    f"{selected_job['title']} at {selected_job['company']} scored {result['match_score']}%. Please review before submission.",
                    channel=notification_channel
                )
            else:
                st.info("Below threshold. No draft was created and nothing was queued.")

with tabs[3]:
    st.subheader("Human approval workflow")
    queue = load_queue()
    if not queue:
        st.info("No items in approval queue yet.")
    else:
        for item in queue:
            job = item.get("job", {})
            app_id = item.get("application_id")
            decision = item.get("approval_decision", "pending")
            with st.expander(f"{job.get('company')} — {job.get('title')} | Score {item.get('match_score')}% | {decision}", expanded=False):
                st.write("Application ID:", app_id)
                st.write("URL:", job.get("url"))
                st.markdown("#### Grounding facts used")
                for fact in item.get("draft", {}).get("grounding_facts", []):
                    st.write(f"- {fact}")
                st.markdown("#### CV summary")
                st.text_area(f"CV summary {app_id}", item.get("draft", {}).get("cv_summary", ""), height=160)
                st.markdown("#### Cover letter")
                st.text_area(f"Cover letter {app_id}", item.get("draft", {}).get("cover_letter", ""), height=260)
                note = st.text_input(f"Reviewer note {app_id}", value=item.get("reviewer_note", ""))
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"Approve for manual submission {app_id}"):
                        updated = update_queue_decision(app_id, "approved_for_manual_submission", note)
                        if updated:
                            updated["status"] = "approved_for_manual_submission"
                            upsert_application(updated)
                            st.success("Approved. User may now submit manually. No automated portal submission was done.")
                with c2:
                    if st.button(f"Reject {app_id}"):
                        updated = update_queue_decision(app_id, "rejected", note)
                        if updated:
                            updated["status"] = "rejected"
                            upsert_application(updated)
                            st.warning("Rejected and logged.")

with tabs[4]:
    st.subheader("Application tracker and reporting")
    tracker = load_tracker()
    if tracker:
        rows = []
        for item in tracker:
            job = item.get("job", {})
            rows.append({
                "company": job.get("company"),
                "title": job.get("title"),
                "score": item.get("match_score"),
                "status": item.get("status"),
                "updated_at": item.get("updated_at")
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df["status"].value_counts())
    else:
        st.info("No applications tracked yet.")

    st.markdown("### Audit log")
    audit_log = load_audit_log()
    if audit_log:
        st.dataframe(pd.DataFrame(audit_log), use_container_width=True)
    else:
        st.info("No audit events yet.")

with tabs[5]:
    st.subheader("Governance controls")
    st.markdown("""
| Control | Status in scaffold |
|---|---|
| Human approval before submission | Enforced |
| No-fabrication drafting | Template-grounded to master profile |
| Portal ToS review | Checklist included |
| DPIA | Template included |
| Credential vault | Environment/secrets pattern included |
| Audit log | Enabled |
| Kill switch | Enabled |
| Auto-submit | Disabled by default |
""")
    st.info(retention_policy_summary())
    st.markdown("See `governance_checklist.md`, `portal_tos_review.md`, and `dpia_template.md` for production readiness.")
