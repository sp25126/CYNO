"""
Multi-Channel Notification System
Supports: Telegram, WhatsApp (Twilio), Email, Discord
"""
import os
import logging
import requests
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)


class MultiChannelNotifier:
    """Send notifications via multiple channels."""
    
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
        self.user_phone = os.getenv("USER_PHONE")
        self.user_email = os.getenv("USER_EMAIL")
        
        # Determine enabled channels
        self.channels = []
        if self.telegram_token and self.telegram_chat_id:
            self.channels.append("telegram")
        if self.twilio_sid and self.user_phone:
            self.channels.append("whatsapp")
        if self.user_email:
            self.channels.append("email")
    
    def send(self, message: str, priority: str = "normal") -> bool:
        """
        Send notification via all enabled channels.
        
        Args:
            message: Message to send
            priority: "low", "normal", "high", "critical"
            
        Returns:
            True if at least one channel succeeded
        """
        results = []
        
        # Format message with priority emoji
        priority_emojis = {
            "low": "ℹ️",
            "normal": "📢",
            "high": "⚠️",
            "critical": "🚨"
        }
        formatted_msg = f"{priority_emojis.get(priority, '📢')} {message}"
        
        # Send via all channels
        if "telegram" in self.channels:
            results.append(self._send_telegram(formatted_msg))
        
        if "whatsapp" in self.channels and priority in ["high", "critical"]:
            # WhatsApp only for important messages (save credits)
            results.append(self._send_whatsapp(formatted_msg))
        
        if "email" in self.channels and priority in ["high", "critical"]:
            results.append(self._send_email("Cyno Notification", formatted_msg))
        
        return any(results)
    
    def _send_telegram(self, message: str) -> bool:
        """Send via Telegram Bot API."""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Telegram notification sent")
                return True
            else:
                logger.error(f"Telegram failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def _send_whatsapp(self, message: str) -> bool:
        """Send via Twilio WhatsApp API."""
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_sid, self.twilio_token)
            
            msg = client.messages.create(
                from_=self.twilio_whatsapp,
                body=message,
                to=self.user_phone
            )
            
            logger.info(f"✅ WhatsApp notification sent: {msg.sid}")
            return True
        except ImportError:
            logger.error("Twilio not installed. Run: pip install twilio")
            return False
        except Exception as e:
            logger.error(f"WhatsApp error: {e}")
            return False
    
    def _send_email(self, subject: str, body: str) -> bool:
        """Send via SMTP (Gmail)."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            gmail_address = os.getenv("GMAIL_ADDRESS")
            gmail_password = os.getenv("GMAIL_APP_PASSWORD")
            
            if not gmail_address or not gmail_password:
                logger.error("Gmail credentials not configured")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = gmail_address
            msg['To'] = self.user_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(gmail_address, gmail_password)
                server.send_message(msg)
            
            logger.info("✅ Email notification sent")
            return True
        except Exception as e:
            logger.error(f"Email error: {e}")
            return False
    
    def send_approval_request(self, change_description: str, change_type: str, expected_impact: str) -> str:
        """
        Send approval request and return request_id for tracking.
        
        Returns:
            request_id: Unique ID to track approval
        """
        import uuid
        request_id = str(uuid.uuid4())[:8]
        
        message = f"""
🤖 <b>Cyno Improvement Request</b>

ID: {request_id}
Type: {change_type}

<b>Proposed Change:</b>
{change_description}

<b>Expected Impact:</b>
{expected_impact}

<b>Reply:</b> YES to approve, NO to reject
        """.strip()
        
        self.send(message, priority="high")
        
        # Store request metadata
        # In real implementation, would save to database
        logger.info(f"Approval request {request_id} sent")
        
        return request_id
    
    def send_daily_report(self, stats: dict):
        """Send daily performance report."""
        message = f"""
📊 <b>Cyno Daily Report</b>

Jobs Found: {stats.get('jobs_found', 0)}
Match Accuracy: {stats.get('match_accuracy', 0)}%
Scrapers Active: {stats.get('active_scrapers', 0)}/{stats.get('total_scrapers', 0)}
Improvements Applied: {stats.get('improvements', 0)}

Status: {'✅ All systems operational' if stats.get('health') == 'HEALTHY' else '⚠️ Some issues detected'}
        """.strip()
        
        self.send(message, priority="normal")
    
    def send_alert(self, alert_type: str, details: str):
        """Send critical alert."""
        message = f"""
🚨 <b>ALERT: {alert_type}</b>

{details}

Auto-recovery in progress...
        """.strip()
        
        self.send(message, priority="critical")


# Quick test function
if __name__ == "__main__":
    notifier = MultiChannelNotifier()
    print(f"Enabled channels: {notifier.channels}")
    
    if notifier.channels:
        notifier.send("🤖 Cyno notification system test!", priority="normal")
    else:
        print("⚠️ No notification channels configured")
        print("\nSetup instructions:")
        print("1. For Telegram: Message @BotFather, create bot, get token")
        print("2. For WhatsApp: Sign up at twilio.com")
        print("3. For Email: Enable Gmail app password")
