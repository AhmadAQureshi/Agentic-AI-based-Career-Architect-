# AI Job Search Agent — Production-Ready MVP Scaffold

This package upgrades the demo MVP into a safer "real-agent" scaffold.

It includes:
- Job source connectors framework: LinkedIn alerts via email/export, company career pages, job board APIs
- LLM drafting interface with strict source grounding
- Email/mobile notification hooks
- Human approval workflow
- Portal Terms-of-Service review register
- Data privacy controls and DPIA template
- Secure credential handling via environment variables / Streamlit secrets
- Monitoring, audit logs and kill switch

## Important safety principle

The agent can draft and recommend, but it must not submit applications automatically unless:
1. the user has approved the exact final CV/cover letter;
2. the portal Terms of Service allows the intended automation;
3. credentials are stored securely;
4. audit logging and kill switch are enabled.

## Run locally

```powershell
cd job_search_agent_real_v1
py -3 -m pip install -r requirements.txt
py -3 -m streamlit run app.py
```

If you use a virtual environment:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `agent_core.py` | Matching, thresholding, approval-queue logic |
| `connectors.py` | Pluggable job-source connectors |
| `drafting.py` | Grounded CV/cover-letter drafting |
| `notifications.py` | Email/mobile notification hooks |
| `storage.py` | Tracker, audit log, queue persistence |
| `privacy.py` | Privacy checks, retention and DPIA helpers |
| `config.example.json` | Source and governance configuration |
| `sample_sources.json` | Example job-source registry |
| `sample_jobs.json` | Example job postings |
| `sample_profile.txt` | Example candidate profile |
| `portal_tos_review.md` | Terms-of-service review checklist |
| `dpia_template.md` | DPIA template |
| `governance_checklist.md` | Human-in-loop and safety controls |
| `.streamlit/secrets.toml.example` | Secure secret format example |

## Deployment notes

For demo: Streamlit Community Cloud.

For personal/private use: Render, Railway, Azure App Service, or a VPS with Docker.

For production:
- do not store real CVs, application history or credentials in GitHub;
- use a database with encryption at rest;
- use a proper secret manager such as cloud key vault;
- run a DPIA before processing real candidate data;
- review every target job portal's Terms of Service before using automated access.
