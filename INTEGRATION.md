# Detailed Integration Guide for Nail Booking System

This document provides detailed instructions on how to integrate the Nail Booking System with Facebook Messenger and Instagram for automated appointment booking.

## Facebook Messenger Integration Details

### Step 1: Register as a Facebook Developer

1. Go to [Facebook for Developers](https://developers.facebook.com/)
2. Sign in with your Facebook account
3. Complete the developer registration process if you haven't already

### Step 2: Create a Facebook App

1. Visit the [Facebook Developer Dashboard](https://developers.facebook.com/apps/)
2. Click "Create App"
3. Select "Business" as the app type
4. Enter your app name (e.g., "NailBookingSystem")
5. Complete the security check and click "Create App"

### Step 3: Configure Messenger Settings

1. In your app dashboard, find and click "Add Products" in the left sidebar
2. Locate "Messenger" and click "Set Up"
3. In the Messenger settings page:
   - Scroll to "Access Tokens" section
   - Select your Facebook Page from the dropdown (create one if needed)
   - Click "Generate Token" to create a Page Access Token
   - Copy and save this token securely as `FB_PAGE_ACCESS_TOKEN`

### Step 4: Set Up Webhooks

1. In the Messenger settings, find the "Webhooks" section
2. Click "Add Callback URL"
3. In the dialog that appears:
   - Webhook URL: Enter your application's webhook URL (e.g., `https://your-app-url.com/fb_webhook`)
   - Verify Token: Create a unique string (e.g., `your_custom_verify_token`) and save it as `FB_VERIFY_TOKEN`
   - Subscription Fields: Select at minimum `messages`, `messaging_postbacks`, and `message_deliveries`
4. Click "Verify and Save"

### Step 5: Subscribe to Events

1. After setting up the webhook, find "Add Subscriptions" dropdown
2. Select your page
3. Choose the events you want to subscribe to (at minimum `messages`, `messaging_postbacks`)
4. Click "Save"

### Step 6: Update Your Application Code

Ensure that your `facebook_messenger.py` file has the following configuration:

```python
def __init__(self):
    self.page_access_token = os.environ.get('FB_PAGE_ACCESS_TOKEN')
    self.verify_token = os.environ.get('FB_VERIFY_TOKEN')
    self.api_version = 'v18.0'  # Update to latest version as needed
    self.base_url = f'https://graph.facebook.com/{self.api_version}'
```

### Step 7: Test Your Integration

1. Go to your Facebook Page
2. Send a message to your Page through Facebook Messenger
3. Check your application logs to ensure the webhook is receiving the message
4. Verify that your application responds correctly

## Instagram Integration Details

### Step 1: Set Up Instagram Professional Account

1. Convert your Instagram account to a Professional account (if not already):
   - Go to your profile and tap on the hamburger menu
   - Select "Settings"
   - Tap "Account"
   - Scroll down and tap "Switch to Professional Account"
   - Choose "Business" as the category
   - Follow the prompts to complete the setup

2. Connect your Instagram Professional account to your Facebook Page:
   - In Instagram settings, tap "Business" or "Creator"
   - Tap "Connect Facebook Page"
   - Select the Facebook Page you used for your Messenger integration

### Step 2: Configure Instagram Graph API

1. Return to your Facebook Developer dashboard
2. Click on your app
3. In the left sidebar, find and click "Add Products"
4. Locate "Instagram Graph API" and click "Set Up"

### Step 3: Get Instagram Business Account ID

1. Go to the [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Generate a user access token with `instagram_basic` and `instagram_manage_messages` permissions
4. Make a GET request to:
   ```
   /{your-facebook-page-id}?fields=instagram_business_account
   ```
5. The response will contain your Instagram Business Account ID
6. Save this ID as `IG_ACCOUNT_ID` in your environment variables

### Step 4: Set Up Instagram Webhooks

1. In your Facebook app dashboard, go to "Webhooks" in the sidebar
2. Click "Add Subscriptions" and select "Instagram"
3. Configure the webhook:
   - Callback URL: Your app's webhook URL (e.g., `https://your-app-url.com/ig_webhook`)
   - Verify Token: Use the same verify token as for Facebook Messenger
   - Subscription Fields: Select at minimum `messages` and `messaging_postbacks`
4. Click "Verify and Save"

### Step 5: Request Permissions

For Instagram messaging integration, you need to submit your app for review by Facebook with the following permissions:

1. `instagram_basic` - To access basic Instagram account information
2. `instagram_manage_messages` - To send and receive Instagram direct messages
3. `pages_messaging` - To send messages using your page

Note: Until your app is approved, you can only send messages to Instagram accounts that are test users or developers of your app.

### Step 6: Update Your Application Code

Ensure that your `instagram_api.py` file has the following configuration:

```python
def __init__(self):
    self.instagram_account_id = os.environ.get('IG_ACCOUNT_ID')
    self.access_token = os.environ.get('FB_PAGE_ACCESS_TOKEN')  # Uses the same token as Messenger
    self.api_version = 'v18.0'  # Update to latest version as needed
    self.base_url = f'https://graph.facebook.com/{self.api_version}'
```

### Step 7: Configure Test Users During Development

While developing and before app approval:

1. Go to your app's roles in the Facebook Developer Dashboard
2. Add "Test Users" for your app (these can be your own accounts)
3. Only these test users will be able to fully interact with your app via Instagram messages

## Environment Variables Summary

Ensure these environment variables are set in your application:

```
# Facebook Messenger Integration
FB_APP_ID=your_facebook_app_id
FB_APP_SECRET=your_facebook_app_secret
FB_PAGE_ID=your_facebook_page_id
FB_PAGE_ACCESS_TOKEN=your_page_access_token
FB_VERIFY_TOKEN=your_custom_verify_token

# Instagram Integration
IG_ACCOUNT_ID=your_instagram_business_account_id

# General
SESSION_SECRET=your_session_secret
DATABASE_URL=your_database_connection_string
```

## Webhooks Processing

The application's webhook routes handle the verification and processing of incoming messages:

### Facebook Messenger Webhook

```python
@app.route('/fb_webhook', methods=['GET', 'POST'])
def fb_webhook():
    if request.method == 'GET':
        # Handle the verification request
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if fb_messenger.verify_webhook(mode, token):
            return challenge
        else:
            return 'Verification failed', 403
    
    elif request.method == 'POST':
        # Handle incoming messages
        data = request.get_json()
        fb_messenger.process_webhook(data)
        return 'OK'
```

### Instagram Webhook

```python
@app.route('/ig_webhook', methods=['GET', 'POST'])
def ig_webhook():
    if request.method == 'GET':
        # Handle the verification request
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if instagram_api.verify_webhook(mode, token):
            return challenge
        else:
            return 'Verification failed', 403
    
    elif request.method == 'POST':
        # Handle incoming messages
        data = request.get_json()
        instagram_api.process_webhook(data)
        return 'OK'
```

## Testing in Production

1. Deploy your application to a production server with HTTPS support
2. Set up proper SSL certificates (required by Facebook)
3. Configure the webhook URLs with your production domain
4. Test the entire flow from message reception to appointment booking

## Common Issues and Troubleshooting

1. **Webhook Verification Fails**
   - Double-check that your verify token matches exactly
   - Ensure your server is accessible from the internet
   - Check that your SSL certificate is valid

2. **Messages Not Being Received**
   - Verify your webhook subscription is active
   - Check your server logs for any errors
   - Ensure your page access token has not expired

3. **API Rate Limiting**
   - Implement proper error handling for rate limiting
   - Add exponential backoff for retries
   - Monitor your API usage in the Facebook Developer Dashboard

4. **Message Sending Fails**
   - Verify your access tokens are correct and not expired
   - Check if you have the necessary permissions
   - Ensure the recipient is a valid user who can receive messages

For additional support, refer to:
- [Facebook Messenger Platform Documentation](https://developers.facebook.com/docs/messenger-platform/)
- [Instagram Graph API Documentation](https://developers.facebook.com/docs/instagram-api/)