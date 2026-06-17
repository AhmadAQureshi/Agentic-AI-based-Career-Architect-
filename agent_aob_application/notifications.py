from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Dict

from storage import audit


def notify_user(subject: str, body: str, channel: str = "audit_only") -> Dict[str, object]:
    """
    Notification hook.

    Supported safe default:
    - audit_only: records the notification event but sends nothing.

    Optional email environment variables:
    - SMTP_HOST
    - SMTP_PORT
    - SMTP_USER
    - SMTP_PASSWORD
    - NOTIFY_TO
    """
    if channel == "audit_only":
        audit("notification_audit_only", {"subject": subject})
        return {"sent": False, "channel": "audit_only", "message": "Notification logged only."}

    if channel == "email":
        required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "NOTIFY_TO"]
        missing = [k for k in required if not os.getenv(k)]
        if missing:
            audit("notification_failed", {"subject": subject, "missing": missing})
            return {"sent": False, "channel": "email", "missing": missing}

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = os.getenv("SMTP_USER")
        msg["To"] = os.getenv("NOTIFY_TO")
        msg.set_content(body)

        with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", "587"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)

        audit("notification_sent", {"subject": subject, "channel": "email"})
        return {"sent": True, "channel": "email"}

    audit("notification_failed", {"subject": subject, "reason": "unknown_channel"})
    return {"sent": False, "channel": channel, "message": "Unknown notification channel."}
