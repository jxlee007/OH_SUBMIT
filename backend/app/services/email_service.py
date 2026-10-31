"""Email service — local capture sink for offline resilience and password resets."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pathlib import Path

from backend.app.core.config import settings

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
EMAIL_LOG_PATH = LOG_DIR / "email.log"


def send_password_reset_email(to_email: str, reset_token: str) -> None:
    """Dispatches a password reset link to local capture sink or relay."""
    reset_url = f"http://localhost:5173/reset-password?token={reset_token}"
    timestamp = datetime.now(timezone.utc).isoformat()
    log_entry = (
        f"[{timestamp}] RECIPIENT: {to_email} | "
        f"SUBJECT: Reset Your Brightloop Password | "
        f"URL: {reset_url}\n"
    )

    # Always log to local email sink for offline evaluation
    with open(EMAIL_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)

    # If SMTP capture / relay is enabled, attempt socket dispatch
    if getattr(settings, "SMTP_RELAY_ENABLED", False):
        try:
            msg = MIMEMultipart()
            msg["From"] = "noreply@brightloop.com"
            msg["To"] = to_email
            msg["Subject"] = "Reset Your Brightloop Password"
            body = f"Click the link to reset your password:\n\n{reset_url}\n\nValid for 30 minutes."
            msg.attach(MIMEText(body, "plain"))

            smtp_host = getattr(settings, "SMTP_HOST", "localhost")
            smtp_port = getattr(settings, "SMTP_PORT", 1025)
            with smtplib.SMTP(smtp_host, smtp_port, timeout=3) as server:
                server.send_message(msg)
        except Exception:
            # Fallback to file sink is preserved
            pass
