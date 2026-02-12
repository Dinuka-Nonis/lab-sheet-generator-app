"""
Email notification system for Lab Sheet Generator V3.0
Separates notification email (university) from authentication (personal)
"""

import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Handles email notifications to users.
    Uses university email for notifications, separate from OneDrive auth.
    """
    
    def __init__(self, config):
        """
        Initialize email notifier.
        
        Args:
            config: Config instance
        """
        self.config = config
        self.user_email = None
        self._load_user_email()
    
    def _load_user_email(self):
        """Load user's notification email from config."""
        config_data = self.config.load_config()
        if config_data:
            self.user_email = config_data.get('user_email')
            if self.user_email:
                logger.info(f"Notifications configured for: {self.user_email}")
            else:
                logger.warning("No notification email configured")
    
    def get_notification_email(self):
        """Get the email address for notifications."""
        return self.user_email
    
    def has_email_configured(self):
        """Check if user has configured an email."""
        return self.user_email is not None and '@' in str(self.user_email)
    
    def send_notification(self, subject, body):
        """
        Send email notification (placeholder for Phase 2).
        
        Args:
            subject: Email subject
            body: Email body (HTML supported)
            
        Returns:
            bool: True if would be sent successfully
        """
        if not self.has_email_configured():
            logger.warning("Cannot send notification: no email configured")
            return False
        
        logger.info(f"📧 Would send to: {self.user_email}")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   (Email sending will be implemented in Phase 2)")
        
        return True