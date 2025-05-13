import requests
import logging
from config import FB_PAGE_ACCESS_TOKEN, FB_VERIFY_TOKEN

logger = logging.getLogger(__name__)

class FacebookMessenger:
    """
    Class for handling Facebook Messenger integration
    """
    
    def __init__(self):
        self.page_access_token = FB_PAGE_ACCESS_TOKEN
        self.verify_token = FB_VERIFY_TOKEN
        self.api_url = "https://graph.facebook.com/v18.0/me/messages"
    
    def verify_webhook(self, mode, token):
        """
        Verify the webhook setup with Facebook
        """
        if mode and token:
            if mode == 'subscribe' and token == self.verify_token:
                logger.info("Webhook verified successfully")
                return True
            else:
                logger.warning(f"Webhook verification failed. Mode: {mode}, Token: {token}")
        return False
    
    def process_webhook(self, data):
        """
        Process incoming webhook data from Facebook
        """
        if data.get('object') == 'page':
            entries = data.get('entry', [])
            messages = []
            
            for entry in entries:
                messaging_events = entry.get('messaging', [])
                
                for event in messaging_events:
                    sender_id = event.get('sender', {}).get('id')
                    
                    if not sender_id:
                        continue
                    
                    if event.get('message'):
                        message_text = event.get('message', {}).get('text')
                        if message_text:
                            logger.info(f"Received message from {sender_id}: {message_text}")
                            messages.append({
                                'sender_id': sender_id,
                                'message': message_text,
                                'timestamp': event.get('timestamp')
                            })
            
            return messages
        
        return []
    
    def send_message(self, recipient_id, message_text):
        """
        Send a message to a user via Facebook Messenger
        """
        if not self.page_access_token:
            logger.error("Missing Facebook Page Access Token")
            return False
        
        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': message_text}
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        params = {
            'access_token': self.page_access_token
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to {recipient_id}")
                return True
            else:
                logger.error(f"Failed to send message. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def get_user_profile(self, user_id):
        """
        Get user profile information from Facebook
        """
        if not self.page_access_token:
            logger.error("Missing Facebook Page Access Token")
            return None
        
        url = f"https://graph.facebook.com/v18.0/{user_id}"
        params = {
            'fields': 'first_name,last_name,profile_pic',
            'access_token': self.page_access_token
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user profile. Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None
