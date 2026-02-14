"""Email service for sending emails via SendGrid/Resend."""

class EmailService:
    """Service for handling email communications."""

    def __init__(self):
        pass

    async def send_email(self, to_email: str, subject: str, body: str) -> dict:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body

        Returns:
            Dict with status and message_id
        """
        # Placeholder implementation
        return {"status": "sent", "message_id": "placeholder"}

    async def send_email_async(
        self,
        to_email: str,
        subject: str,
        body: str,
        communication_id: str | None = None,
    ) -> dict:
        """Compatibility wrapper used by routers."""
        _ = communication_id
        return await self.send_email(to_email=to_email, subject=subject, body=body)
