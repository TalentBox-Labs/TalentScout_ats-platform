"""Email service for sending emails via SendGrid/Resend."""

import logging
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for handling email communications."""

    def __init__(self):
        self.provider = settings.email_provider
        self.from_email = settings.from_email
        self.from_name = settings.from_name

    async def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> Dict[str, Any]:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            html_body: HTML email body (optional)

        Returns:
            Dict with status and message_id
        """
        try:
            if self.provider == "sendgrid":
                return await self._send_via_sendgrid(to_email, subject, body, html_body)
            elif self.provider == "resend":
                return await self._send_via_resend(to_email, subject, body, html_body)
            else:
                logger.warning(f"Unknown email provider: {self.provider}")
                return {"status": "error", "message": "Unknown email provider"}
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"status": "error", "message": str(e)}

    async def _send_via_sendgrid(self, to_email: str, subject: str, body: str, html_body: str = None) -> Dict[str, Any]:
        """Send email via SendGrid."""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content

            sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
            from_email = Email(self.from_email, self.from_name)
            to_email_obj = To(to_email)
            content = Content("text/plain", body)

            mail = Mail(from_email, to_email_obj, subject, content)

            if html_body:
                from sendgrid.helpers.mail import HtmlContent
                mail.add_content(HtmlContent(html_body))

            response = sg.send(mail)

            return {
                "status": "sent",
                "message_id": response.headers.get("X-Message-Id", "unknown"),
                "status_code": response.status_code
            }
        except ImportError:
            logger.error("SendGrid not installed")
            return {"status": "error", "message": "SendGrid not installed"}
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return {"status": "error", "message": str(e)}

    async def _send_via_resend(self, to_email: str, subject: str, body: str, html_body: str = None) -> Dict[str, Any]:
        """Send email via Resend."""
        try:
            import resend

            resend.api_key = settings.resend_api_key

            email_data = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "text": body,
            }

            if html_body:
                email_data["html"] = html_body

            response = resend.Emails.send(email_data)

            return {
                "status": "sent",
                "message_id": response.get("id", "unknown")
            }
        except ImportError:
            logger.error("Resend not installed")
            return {"status": "error", "message": "Resend not installed"}
        except Exception as e:
            logger.error(f"Resend error: {e}")
            return {"status": "error", "message": str(e)}

    async def send_password_reset_email(self, to_email: str, reset_token: str) -> Dict[str, Any]:
        """Send password reset email."""
        reset_url = f"{settings.frontend_url}/auth/reset-password?token={reset_token}"

        subject = "Reset Your Password - ATS Platform"
        body = f"""
        Hi,

        You requested to reset your password for your ATS Platform account.

        Please click the link below to reset your password:
        {reset_url}

        This link will expire in 1 hour.

        If you didn't request this password reset, please ignore this email.

        Best regards,
        ATS Platform Team
        """

        html_body = f"""
        <html>
        <body>
            <h2>Reset Your Password</h2>
            <p>Hi,</p>
            <p>You requested to reset your password for your ATS Platform account.</p>
            <p>Please click the link below to reset your password:</p>
            <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this password reset, please ignore this email.</p>
            <br>
            <p>Best regards,<br>ATS Platform Team</p>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, body, html_body)

    async def send_email_async(self, to_email: str, subject: str, body: str, html_body: str = None, communication_id: str = None) -> Dict[str, Any]:
        """
        Send an email asynchronously (queue for background processing).
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            html_body: HTML email body (optional)
            communication_id: Associated communication record ID
            
        Returns:
            Dict with status and message_id
        """
        # For now, just call the synchronous version
        # In production, this should queue to Celery/RabbitMQ
        return await self.send_email(to_email, subject, body, html_body)