# DPIA Template — AI Job Search Agent

## 1. Processing purpose

Assist a user with monitoring job opportunities, scoring job fit, preparing source-grounded application drafts, and tracking application progress.

## 2. Personal data processed

- CV/profile data
- Employment history
- Education and certifications
- Skills and preferences
- Job applications and statuses
- Email/mobile notification destination

## 3. Data subjects

Candidate / job seeker.

## 4. Lawful basis / consent

Document the user's explicit consent and ability to stop processing.

## 5. Risks

| Risk | Mitigation |
|---|---|
| Fabricated CV claims | Grounding verifier + human approval |
| Unauthorized submission | Auto-submit disabled + approval workflow |
| Credential leak | Secret manager + least privilege |
| Portal ToS breach | Per-source ToS review |
| Excessive data retention | Retention policy + deletion workflow |
| Prompt injection from job descriptions | Treat job descriptions as untrusted input |
| Bias in recommendations | Explain score and allow user override |

## 6. Security controls

- Encryption at rest for production database
- HTTPS
- Role-based access if multi-user
- Audit logs
- Kill switch
- Backups
- Data deletion process

## 7. Human oversight

The user approves every application before submission.
