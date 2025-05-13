# Nail Booking System

A Python Flask-based booking system for nail beauticians that integrates with Facebook Messenger and Instagram to automate appointment scheduling.

## Features

- User authentication system for nail beauticians
- Dashboard with appointment overview
- Calendar integration for easy scheduling
- Client management
- Automated messaging through Facebook Messenger and Instagram
- Appointment scheduling and management
- Reporting and analytics

## Technical Stack

- **Backend**: Python with Flask framework
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Frontend**: Bootstrap CSS framework
- **Authentication**: Flask-Login
- **Calendar**: FullCalendar.js
- **Messaging APIs**: Facebook Messenger API, Instagram Graph API

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nail-booking-system.git
   cd nail-booking-system
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
   ```bash
   # Database configuration
   export DATABASE_URL=postgresql://username:password@localhost/nailbooking
   
   # Facebook and Instagram integration
   export FB_APP_ID=your_facebook_app_id
   export FB_APP_SECRET=your_facebook_app_secret
   export FB_PAGE_ID=your_facebook_page_id
   export FB_PAGE_ACCESS_TOKEN=your_page_access_token
   export IG_ACCOUNT_ID=your_instagram_account_id
   
   # Flask session security
   export SESSION_SECRET=your_session_secret
   ```

4. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the application:
   ```bash
   python main.py
   ```

## Facebook Messenger Integration

### Prerequisites

1. Create a Facebook Developer Account: Visit [Facebook for Developers](https://developers.facebook.com/) and create an account.

2. Create a Facebook App:
   - Go to the [Facebook Developer Dashboard](https://developers.facebook.com/apps/)
   - Click "Create App"
   - Select "Business" as the app type
   - Fill in the required information and create your app

3. Set up Messenger:
   - In your app dashboard, add the "Messenger" product
   - Go to the Messenger settings

### Configuration Steps

1. **Page Setup**:
   - Connect your Facebook Page to your app in the Messenger settings
   - Generate a Page Access Token and save it as `FB_PAGE_ACCESS_TOKEN` in your environment variables

2. **Webhooks Setup**:
   - In the Webhooks section, click "Add Callback URL"
   - Enter your app's webhook URL: `https://yourdomain.com/fb_webhook`
   - Enter your verify token (create a unique string and save it for verification)
   - Select subscription fields: `messages`, `messaging_postbacks`, `message_deliveries`

3. **Event Subscriptions**:
   - Subscribe your page to the webhook events

4. **Update your application configuration**:
   ```python
   # In facebook_messenger.py
   self.page_access_token = os.environ.get('FB_PAGE_ACCESS_TOKEN')
   self.verify_token = os.environ.get('FB_VERIFY_TOKEN')
   ```

5. **Test your integration**:
   - Use the Facebook Messenger tester in the developer console
   - Send a message to your page and check if your application responds

## Instagram Integration

### Prerequisites

1. Have a Facebook Page connected to an Instagram Professional account (Business or Creator)

2. Set up Instagram Graph API:
   - In your Facebook App dashboard, add the "Instagram Graph API" product
   - Connect your Instagram Professional account to your Facebook Page

### Configuration Steps

1. **Get Instagram Account ID**:
   - Use the Graph API Explorer to get your Instagram Business Account ID
   - Save it as `IG_ACCOUNT_ID` in your environment variables

2. **Set up Instagram Webhooks**:
   - In the Webhooks section of your app, add a subscription for Instagram
   - Enter your app's webhook URL: `https://yourdomain.com/ig_webhook`
   - Use the same verify token as for Facebook Messenger
   - Subscribe to relevant fields: `messages`, `messaging_postbacks`

3. **Update your application configuration**:
   ```python
   # In instagram_api.py
   self.instagram_account_id = os.environ.get('IG_ACCOUNT_ID')
   self.access_token = os.environ.get('FB_PAGE_ACCESS_TOKEN')  # Uses the same token
   ```

4. **Permissions and Scopes**:
   - Request the following permissions for your app:
     - `instagram_basic`
     - `instagram_manage_messages`
     - `pages_messaging`

5. **Test your integration**:
   - Send a direct message to your Instagram business account
   - Check if your application processes and responds to the message

## Important Notes

1. **Webhook Verification**: Facebook and Instagram will send a verification request to your webhook endpoints when you first set them up. Your application must respond correctly to these verification requests.

2. **Rate Limits**: Be aware of Facebook and Instagram API rate limits. Implement proper error handling and retry mechanisms.

3. **Message Types**: Different message types (text, attachments, quick replies) require different handling. Refer to the messaging.py module to see how different message types are processed.

4. **Testing in Development**: Use ngrok or a similar service to expose your local development server to the internet for webhook testing.

5. **Production Deployment**: When deploying to production, ensure you have proper SSL certificates as Facebook and Instagram require HTTPS for webhooks.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.