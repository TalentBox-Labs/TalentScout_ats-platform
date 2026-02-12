<<<<<<< HEAD
"""
Email service for sending transactional emails.
"""
from typing import Optional, Dict, Any
import asyncio
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import settings


class EmailService:
    """
    Service for sending emails using SendGrid.
    """
    
    def __init__(self):
        self.client = SendGridAPIClient(api_key=settings.sendgrid_api_key)
    
    async def send_email_async(
        self,
        to_email: str,
        subject: str,
        body: str,
        communication_id: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send email asynchronously.
=======
from typing import Dict, List, Optional
from datetime import datetime

class EmailService:
    """
    Email service for sending notifications and communications
    """
    
    def __init__(self):
        # TODO: Initialize email provider (SendGrid, Resend, etc.)
        self.sender_email = "noreply@atsplatform.com"
        self.sender_name = "ATS Platform"
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict:
        """
        Send a single email
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
        
        Args:
            to_email: Recipient email address
            subject: Email subject
<<<<<<< HEAD
            body: Email body (HTML or plain text)
            communication_id: ID of communication record for tracking
            from_email: Sender email address
            from_name: Sender name
=======
            html_content: HTML email body
            text_content: Plain text version (optional)
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
            
        Returns:
            Dict with status and message_id
        """
<<<<<<< HEAD
        try:
            # Create mail object
            message = Mail(
                from_email=from_email or settings.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=body
            )
            
            if from_name:
                message.from_email.name = from_name
            
            # Send email
            response = self.client.send(message)
            
            return {
                "status": "sent",
                "message_id": response.headers.get('X-Message-Id'),
                "status_code": response.status_code
            }
            
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def send_bulk_email(
        self,
        recipients: list[str],
        subject: str,
        body: str,
        personalization: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send bulk emails with personalization.
        
        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            body: Email body template
            personalization: Dict mapping email to personalization variables
            
        Returns:
            Dict with status and results
        """
        results = []
        
        for recipient in recipients:
            # Personalize body if variables provided
            personalized_body = body
            if personalization and recipient in personalization:
                for key, value in personalization[recipient].items():
                    personalized_body = personalized_body.replace(f"{{{{{key}}}}}", str(value))
            
            result = await self.send_email_async(
                to_email=recipient,
                subject=subject,
                body=personalized_body,
            )
            results.append(result)
        
        return {
            "status": "completed",
            "total_sent": len(results),
            "results": results,
        }
    
    def track_email_opens(self, message_id: str) -> bool:
        """
        Check if email was opened (via tracking pixel).
        
        Args:
            message_id: Email message ID
            
        Returns:
            True if email was opened
        """
        # TODO: Implement email open tracking
        return False
    
    def track_email_clicks(self, message_id: str) -> int:
        """
        Get number of clicks in email.
        
        Args:
            message_id: Email message ID
            
        Returns:
            Number of clicks
        """
        # TODO: Implement email click tracking
        return 0
=======
        # TODO: Implement email sending
        return {
            "status": "sent",
            "message_id": "placeholder",
            "timestamp": datetime.now().isoformat()
        }
    
    async def send_bulk_emails(
        self,
        recipients: List[str],
        subject: str,
        html_content: str
    ) -> Dict:
        """
        Send emails to multiple recipients
        """
        # TODO: Implement bulk email sending
        return {
            "status": "sent",
            "count": len(recipients)
        }
    
    async def send_application_received(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str
    ) -> Dict:
        """
        Send application received confirmation
        """
        subject = f"Application Received - {job_title}"
        html_content = f"""
        <h2>Thank you for your application!</h2>
        <p>Hi {candidate_name},</p>
        <p>We have received your application for the position of {job_title}.</p>
        <p>Our team will review your application and get back to you soon.</p>
        <p>Best regards,<br>The Hiring Team</p>
        """
        
        return await self.send_email(candidate_email, subject, html_content)
    
    async def send_interview_invitation(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        interview_datetime: datetime,
        meeting_link: Optional[str] = None
    ) -> Dict:
        """
        Send interview invitation
        """
        subject = f"Interview Invitation - {job_title}"
        
        meeting_info = f"<p>Meeting Link: <a href='{meeting_link}'>{meeting_link}</a></p>" if meeting_link else ""
        
        html_content = f"""
        <h2>Interview Invitation</h2>
        <p>Hi {candidate_name},</p>
        <p>We would like to invite you for an interview for the position of {job_title}.</p>
        <p><strong>Date and Time:</strong> {interview_datetime.strftime('%B %d, %Y at %I:%M %p')}</p>
        {meeting_info}
        <p>Please confirm your availability.</p>
        <p>Best regards,<br>The Hiring Team</p>
        """
        
        return await self.send_email(candidate_email, subject, html_content)
    
    async def send_rejection(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        personalized_message: Optional[str] = None
    ) -> Dict:
        """
        Send rejection email
        """
        subject = f"Application Update - {job_title}"
        
        custom_message = f"<p>{personalized_message}</p>" if personalized_message else ""
        
        html_content = f"""
        <h2>Application Update</h2>
        <p>Hi {candidate_name},</p>
        <p>Thank you for your interest in the {job_title} position.</p>
        <p>After careful consideration, we have decided to move forward with other candidates whose qualifications more closely match our current needs.</p>
        {custom_message}
        <p>We appreciate the time you invested in the application process and wish you the best in your job search.</p>
        <p>Best regards,<br>The Hiring Team</p>
        """
        
        return await self.send_email(candidate_email, subject, html_content)
    
    async def send_offer(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        offer_details: Dict
    ) -> Dict:
        """
        Send job offer
        """
        subject = f"Job Offer - {job_title}"
        html_content = f"""
        <h2>Congratulations! Job Offer</h2>
        <p>Hi {candidate_name},</p>
        <p>We are pleased to offer you the position of {job_title}.</p>
        <p>Please review the attached offer letter for details.</p>
        <p>Best regards,<br>The Hiring Team</p>
        """
        
        return await self.send_email(candidate_email, subject, html_content)
    
    def generate_template(
        self,
        template_name: str,
        variables: Dict
    ) -> str:
        """
        Generate email from template with variables
        """
        # TODO: Implement template system
        return ""
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
