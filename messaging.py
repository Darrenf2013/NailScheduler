import re
import logging
import datetime
from models import Client, MessageThread, Message, Appointment, TimeSlot
from app import db
from facebook_messenger import FacebookMessenger
from instagram_api import InstagramAPI
from config import RESPONSE_TEMPLATES, DEFAULT_APPOINTMENT_DURATION

logger = logging.getLogger(__name__)

class MessageHandler:
    """
    Class for handling messaging logic across platforms
    """
    
    def __init__(self):
        self.fb_messenger = FacebookMessenger()
        self.instagram = InstagramAPI()
        
    def process_message(self, sender_id, message_text, platform, user_id=None):
        """
        Process an incoming message and determine appropriate response
        """
        logger.info(f"Processing message from {platform}: {message_text}")
        
        # Get or create client record
        client = self._get_or_create_client(sender_id, platform)
        
        # Get or create message thread
        thread = self._get_or_create_thread(client.id, sender_id, platform)
        
        # Save the incoming message
        message = Message(
            thread_id=thread.id,
            content=message_text,
            is_from_client=True
        )
        db.session.add(message)
        db.session.commit()
        
        # Generate a response based on message content
        response = self._generate_response(message_text, client, thread, user_id)
        
        # Save the outgoing message
        if response:
            out_message = Message(
                thread_id=thread.id,
                content=response,
                is_from_client=False
            )
            db.session.add(out_message)
            db.session.commit()
            
            # Send the response via appropriate platform
            self._send_platform_message(sender_id, response, platform)
            
        return response
    
    def _get_or_create_client(self, sender_id, platform):
        """
        Get or create a client record based on the messaging platform ID
        """
        client = None
        
        if platform == 'messenger':
            client = Client.query.filter_by(messenger_id=sender_id).first()
        elif platform == 'instagram':
            client = Client.query.filter_by(instagram_id=sender_id).first()
            
        if not client:
            # Create new client
            client = Client(platform=platform)
            
            if platform == 'messenger':
                client.messenger_id = sender_id
                # Try to get profile info from Facebook
                profile = self.fb_messenger.get_user_profile(sender_id)
                if profile:
                    client.name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
            
            elif platform == 'instagram':
                client.instagram_id = sender_id
                # Try to get profile info from Instagram
                profile = self.instagram.get_user_profile(sender_id)
                if profile:
                    client.name = profile.get('username', '')
            
            db.session.add(client)
            db.session.commit()
        
        return client
    
    def _get_or_create_thread(self, client_id, platform_thread_id, platform):
        """
        Get or create a message thread for the conversation
        """
        thread = MessageThread.query.filter_by(
            client_id=client_id,
            platform=platform,
            platform_thread_id=platform_thread_id
        ).first()
        
        if not thread:
            thread = MessageThread(
                client_id=client_id,
                platform=platform,
                platform_thread_id=platform_thread_id
            )
            db.session.add(thread)
            db.session.commit()
        
        # Update last message timestamp
        thread.last_message_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return thread
    
    def _generate_response(self, message_text, client, thread, user_id=None):
        """
        Generate an appropriate response based on the message content
        """
        # Convert message to lowercase for easier matching
        message_lower = message_text.lower()
        
        # Check if this is a greeting
        if any(greeting in message_lower for greeting in ['hi', 'hello', 'hey', 'good morning', 'good afternoon']):
            return RESPONSE_TEMPLATES['greeting']
        
        # Check if this is a service inquiry
        if any(keyword in message_lower for keyword in ['service', 'price', 'cost', 'offer', 'do you do']):
            return RESPONSE_TEMPLATES['service_inquiry']
        
        # Check if this is a booking request
        date_pattern = re.compile(r'(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}(?:st|nd|rd|th)?(?:\s+of\s+)?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+\d{4})?|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)')
        time_pattern = re.compile(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)')
        
        # If no user_id provided, we can't check availability
        if not user_id:
            if 'book' in message_lower or 'appointment' in message_lower:
                return RESPONSE_TEMPLATES['booking_inquiry']
            return "Thank you for your message! I'll respond as soon as possible."
        
        # If message contains date and time information, handle as a booking request
        date_matches = date_pattern.findall(message_lower)
        time_matches = time_pattern.findall(message_lower)
        
        if ('book' in message_lower or 'appointment' in message_lower or 'schedule' in message_lower or 'available' in message_lower) and (date_matches or time_matches):
            # Parse the date and time from the message
            requested_date, requested_time = self._parse_date_time(date_matches, time_matches)
            
            if requested_date and requested_time:
                # Check if the requested time slot is available
                is_available, available_slots = self._check_availability(user_id, requested_date, requested_time)
                
                if is_available:
                    # Create a pending appointment
                    end_time = (datetime.datetime.combine(datetime.date.today(), requested_time) + 
                                datetime.timedelta(minutes=DEFAULT_APPOINTMENT_DURATION)).time()
                    
                    new_appointment = Appointment(
                        user_id=user_id,
                        client_id=client.id,
                        date=requested_date,
                        start_time=requested_time,
                        end_time=end_time,
                        status='confirmed',
                        service_type='Nail Service'  # Default service type
                    )
                    
                    db.session.add(new_appointment)
                    
                    # Update thread status
                    thread.status = 'completed'
                    db.session.commit()
                    
                    # Format the confirmation message
                    formatted_date = requested_date.strftime("%A, %B %d")
                    formatted_time = requested_time.strftime("%I:%M %p")
                    
                    return RESPONSE_TEMPLATES['booking_confirmed'].format(
                        date=formatted_date,
                        time=formatted_time
                    )
                else:
                    # Format available slots
                    slots_text = ""
                    if available_slots:
                        slots_text = ", ".join([f"{slot['date'].strftime('%A, %B %d')} at {slot['time'].strftime('%I:%M %p')}" 
                                              for slot in available_slots[:3]])
                    else:
                        slots_text = "No available slots in the next few days"
                    
                    return RESPONSE_TEMPLATES['booking_unavailable'].format(
                        available_slots=slots_text
                    )
        
        # Default response
        return "Thank you for your message! I'll help you schedule your nail appointment. Let me know what day and time works best for you."
    
    def _parse_date_time(self, date_matches, time_matches):
        """
        Parse date and time from message matches
        """
        requested_date = None
        requested_time = None
        
        today = datetime.date.today()
        
        # Parse date
        if date_matches:
            date_str = date_matches[0].lower()
            
            if date_str == 'today':
                requested_date = today
            elif date_str == 'tomorrow':
                requested_date = today + datetime.timedelta(days=1)
            elif date_str in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                # Map day name to number (0=Monday, 6=Sunday)
                day_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
                           'friday': 4, 'saturday': 5, 'sunday': 6}
                target_day = day_map[date_str]
                current_day = today.weekday()
                days_ahead = (target_day - current_day) % 7
                
                # If days_ahead is 0, we mean next week, not today
                if days_ahead == 0:
                    days_ahead = 7
                    
                requested_date = today + datetime.timedelta(days=days_ahead)
            else:
                # Try to parse more complex date formats
                try:
                    # Handle formats like MM/DD or MM/DD/YYYY
                    if '/' in date_str or '-' in date_str:
                        separator = '/' if '/' in date_str else '-'
                        parts = date_str.split(separator)
                        
                        if len(parts) == 2:
                            month, day = int(parts[0]), int(parts[1])
                            year = today.year
                            requested_date = datetime.date(year, month, day)
                        elif len(parts) == 3:
                            month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                            if year < 100:  # Assume 2-digit year
                                year += 2000
                            requested_date = datetime.date(year, month, day)
                except (ValueError, IndexError):
                    pass
        
        # Parse time
        if time_matches:
            time_str = time_matches[0].lower()
            
            try:
                # Handle formats like 3pm, 3:30pm, 15:30
                if 'am' in time_str or 'pm' in time_str:
                    # 12-hour format
                    time_str = time_str.replace(' ', '')
                    is_pm = 'pm' in time_str
                    time_str = time_str.replace('am', '').replace('pm', '')
                    
                    if ':' in time_str:
                        hour, minute = map(int, time_str.split(':'))
                    else:
                        hour, minute = int(time_str), 0
                    
                    if is_pm and hour < 12:
                        hour += 12
                    elif not is_pm and hour == 12:
                        hour = 0
                else:
                    # 24-hour format or without am/pm
                    if ':' in time_str:
                        hour, minute = map(int, time_str.split(':'))
                    else:
                        hour, minute = int(time_str), 0
                        
                    # Assume times like "3" or "11" without am/pm are during business hours
                    if hour < 8:  # Assuming business starts after 8am
                        hour += 12
                        
                requested_time = datetime.time(hour, minute)
            except (ValueError, IndexError):
                pass
        
        return requested_date, requested_time
    
    def _check_availability(self, user_id, date, time):
        """
        Check if the requested time slot is available
        """
        # Convert time to datetime for easier comparison
        request_datetime = datetime.datetime.combine(date, time)
        
        # Calculate end time based on default appointment duration
        end_datetime = request_datetime + datetime.timedelta(minutes=DEFAULT_APPOINTMENT_DURATION)
        end_time = end_datetime.time()
        
        # Check if there's an existing appointment that overlaps
        existing_appointment = Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.date == date,
            Appointment.status != 'cancelled',
            # Check for time overlap
            ((Appointment.start_time <= time) & (Appointment.end_time > time)) |
            ((Appointment.start_time < end_time) & (Appointment.end_time >= end_time)) |
            ((Appointment.start_time >= time) & (Appointment.end_time <= end_time))
        ).first()
        
        if existing_appointment:
            # Time slot is not available
            # Find alternative available time slots
            available_slots = self._find_available_slots(user_id, date, 3)  # Find 3 alternatives
            return False, available_slots
        
        # Check if the beautician has made this time slot available
        available_time_slot = TimeSlot.query.filter(
            TimeSlot.user_id == user_id,
            TimeSlot.date == date,
            TimeSlot.start_time <= time,
            TimeSlot.end_time >= end_time,
            TimeSlot.is_available == True
        ).first()
        
        # If no specific time slot is set for this time, check if there's any availability for the day
        if not available_time_slot:
            day_slots = TimeSlot.query.filter(
                TimeSlot.user_id == user_id,
                TimeSlot.date == date,
                TimeSlot.is_available == True
            ).all()
            
            if not day_slots:
                # No availability set for this day
                # Find alternative days with availability
                next_days = [(date + datetime.timedelta(days=i)) for i in range(1, 8)]
                available_slots = []
                
                for next_date in next_days:
                    slots = self._find_available_slots(user_id, next_date, 1)
                    if slots:
                        available_slots.extend(slots)
                        if len(available_slots) >= 3:
                            break
                            
                return False, available_slots
            
            # Check if requested time falls within any of the day's available slots
            for slot in day_slots:
                if slot.start_time <= time and slot.end_time >= end_time:
                    return True, []
            
            # Requested time doesn't fall within available slots
            # Suggest available slots for the day
            available_slots = [{'date': date, 'time': slot.start_time} for slot in day_slots]
            return False, available_slots
        
        # The requested time slot is available
        return True, []
    
    def _find_available_slots(self, user_id, date, limit=3):
        """
        Find available time slots for a given date
        """
        # Get all time slots for the day
        time_slots = TimeSlot.query.filter(
            TimeSlot.user_id == user_id,
            TimeSlot.date == date,
            TimeSlot.is_available == True
        ).all()
        
        # Get existing appointments for the day
        appointments = Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.date == date,
            Appointment.status != 'cancelled'
        ).all()
        
        available_slots = []
        
        for slot in time_slots:
            # Check if slot overlaps with any appointment
            is_available = True
            
            for appointment in appointments:
                # Check for overlap
                if ((slot.start_time <= appointment.start_time and slot.end_time > appointment.start_time) or
                    (slot.start_time < appointment.end_time and slot.end_time >= appointment.end_time) or
                    (slot.start_time >= appointment.start_time and slot.end_time <= appointment.end_time)):
                    is_available = False
                    break
            
            if is_available:
                # If slot is longer than default duration, create multiple available slots
                slot_duration = datetime.datetime.combine(date, slot.end_time) - datetime.datetime.combine(date, slot.start_time)
                slot_minutes = slot_duration.total_seconds() / 60
                
                if slot_minutes >= DEFAULT_APPOINTMENT_DURATION:
                    current_time = datetime.datetime.combine(date, slot.start_time)
                    end_datetime = datetime.datetime.combine(date, slot.end_time)
                    
                    # Create slots at hourly intervals
                    while current_time + datetime.timedelta(minutes=DEFAULT_APPOINTMENT_DURATION) <= end_datetime:
                        available_slots.append({
                            'date': date,
                            'time': current_time.time()
                        })
                        
                        if len(available_slots) >= limit:
                            return available_slots
                            
                        # Move to next interval (hourly)
                        current_time += datetime.timedelta(hours=1)
                else:
                    available_slots.append({
                        'date': date,
                        'time': slot.start_time
                    })
                    
                    if len(available_slots) >= limit:
                        break
        
        return available_slots
    
    def _send_platform_message(self, recipient_id, message, platform):
        """
        Send a message through the appropriate platform
        """
        if platform == 'messenger':
            return self.fb_messenger.send_message(recipient_id, message)
        elif platform == 'instagram':
            return self.instagram.send_direct_message(recipient_id, message)
        else:
            logger.error(f"Unknown platform: {platform}")
            return False
