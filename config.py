import os

# Facebook Messenger API
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "nail-booking-verify-token")

# Instagram Graph API
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN")
IG_APP_ID = os.environ.get("IG_APP_ID")
IG_APP_SECRET = os.environ.get("IG_APP_SECRET")

# Application Settings
DEFAULT_APPOINTMENT_DURATION = 60  # minutes
BUSINESS_HOURS = {
    "Monday": {"start": "09:00", "end": "17:00"},
    "Tuesday": {"start": "09:00", "end": "17:00"},
    "Wednesday": {"start": "09:00", "end": "17:00"},
    "Thursday": {"start": "09:00", "end": "17:00"},
    "Friday": {"start": "09:00", "end": "17:00"},
    "Saturday": {"start": "10:00", "end": "15:00"},
    "Sunday": {"start": None, "end": None}  # Closed
}

# Response Templates
RESPONSE_TEMPLATES = {
    "booking_confirmed": "Great! Your nail appointment has been confirmed for {date} at {time}. See you then! 💅",
    "booking_unavailable": "Sorry, I'm not available at that time. These are my available slots: {available_slots}. Would any of these work for you?",
    "booking_inquiry": "I'd be happy to book you in! What day and time works best for you?",
    "greeting": "Hi there! Thanks for reaching out to my nail service. How can I help you today?",
    "service_inquiry": "I offer a variety of nail services including manicures, pedicures, and nail art. Would you like to see my full service list and prices?"
}
