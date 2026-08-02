"""AttritionIQ — Email Utility"""

import structlog
from app.config import settings

logger = structlog.get_logger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    attachments: list = None,
) -> bool:
    """Send an email using SMTP or API service."""
    if not settings.EMAIL_ENABLED:
        logger.info("Email service disabled", to=to_email, subject=subject)
        return True

    try:
        logger.info("Sending email", to=to_email, subject=subject)
        # Integration point for FastAPI-Mail or SendGrid/SES
        return True
    except Exception as e:
        logger.error("Failed to send email", error=str(e))
        return False
