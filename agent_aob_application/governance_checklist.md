# Governance Checklist — AI Job Search Agent

## Non-negotiable controls

- [ ] Human approval required before every application submission.
- [ ] Auto-submit disabled by default.
- [ ] No fabricated achievements, skills, degrees, employers, dates or certifications.
- [ ] Drafting grounded only in approved master profile, CV and user-approved history.
- [ ] Audit log enabled for: source fetch, match decision, draft generation, notification, approval/rejection.
- [ ] Kill switch tested before production.
- [ ] Credential storage uses environment variables or secret manager, never plaintext files.
- [ ] Data retention period defined.
- [ ] User can export and delete profile/application data.
- [ ] Portal Terms-of-Service review completed before using automated access.
- [ ] DPIA completed before processing real personal data at scale.

## Human-in-the-loop rule

The agent may:
- monitor sources;
- score jobs;
- draft CV/cover letter;
- notify the user;
- track application status.

The agent must not:
- invent candidate experience;
- submit without explicit approval;
- bypass portal rules;
- store passwords in code;
- scrape sites without ToS/legal approval.
