import requests
import logging
from config import IG_ACCESS_TOKEN, IG_APP_ID, IG_APP_SECRET

logger = logging.getLogger(__name__)

class InstagramAPI:
    """
    Class for handling Instagram Graph API integration
    """
    
    def __init__(self):
        self.access_token = IG_ACCESS_TOKEN
        self.app_id = IG_APP_ID
        self.app_secret = IG_APP_SECRET
        self.api_base_url = "https://graph.facebook.com/v18.0"
    
    def send_direct_message(self, user_id, message_text):
        """
        Send a direct message to a user on Instagram
        Note: Instagram Graph API has limitations on sending direct messages
        and requires advanced permissions
        """
        if not self.access_token:
            logger.error("Missing Instagram Access Token")
            return False
        
        # This is a simplified version - Instagram DM API is complex
        # In a real implementation, you would need to:
        # 1. Create a message container
        # 2. Send the message to the container
        
        try:
            # Example API call - this is placeholder code
            # Real implementation would need to follow Meta's documentation
            url = f"{self.api_base_url}/{user_id}/messages"
            params = {
                'recipient': {'id': user_id},
                'message': {'text': message_text},
                'access_token': self.access_token
            }
            
            response = requests.post(url, json=params)
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to Instagram user {user_id}")
                return True
            else:
                logger.error(f"Failed to send Instagram message. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Instagram message: {str(e)}")
            return False
    
    def process_webhook(self, data):
        """
        Process incoming webhook data from Instagram
        """
        logger.debug(f"Processing Instagram webhook data: {data}")
        
        try:
            if data.get('object') == 'instagram':
                entries = data.get('entry', [])
                messages = []
                
                for entry in entries:
                    # Process Instagram messages
                    # Structure depends on what webhook events you're subscribed to
                    messaging_items = entry.get('messaging', [])
                    
                    for item in messaging_items:
                        sender_id = item.get('sender', {}).get('id')
                        
                        if not sender_id:
                            continue
                        
                        if item.get('message'):
                            message_text = item.get('message', {}).get('text')
                            if message_text:
                                logger.info(f"Received Instagram message from {sender_id}: {message_text}")
                                messages.append({
                                    'sender_id': sender_id,
                                    'message': message_text,
                                    'timestamp': item.get('timestamp')
                                })
                
                return messages
            
            return []
            
        except Exception as e:
            logger.error(f"Error processing Instagram webhook: {str(e)}")
            return []
    
    def get_user_profile(self, user_id):
        """
        Get Instagram user profile information
        """
        if not self.access_token:
            logger.error("Missing Instagram Access Token")
            return None
        
        url = f"{self.api_base_url}/{user_id}"
        params = {
            'fields': 'username,profile_picture_url',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get Instagram user profile. Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Instagram user profile: {str(e)}")
            return None
