from app import db
from flask_login import UserMixin
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users_table'  # Avoid using 'user' which is a reserved keyword
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    business_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    
    # Relationships
    time_slots = db.relationship('TimeSlot', backref='user', lazy=True)
    appointments = db.relationship('Appointment', backref='beautician', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        # If password_hash is None return False
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    messenger_id = db.Column(db.String(120), nullable=True)
    instagram_id = db.Column(db.String(120), nullable=True)
    platform = db.Column(db.String(20), nullable=True)  # 'messenger', 'instagram', 'direct'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='client', lazy=True)


class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<TimeSlot: {self.date} {self.start_time}-{self.end_time}>"


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    service_type = db.Column(db.String(120))
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='confirmed')  # 'confirmed', 'cancelled', 'completed'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Appointment: {self.client.name} on {self.date} at {self.start_time}>"


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f"<Service: {self.name} ({self.duration} min)>"


class MessageThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    platform = db.Column(db.String(20), nullable=False)  # 'messenger' or 'instagram'
    platform_thread_id = db.Column(db.String(120), nullable=False)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # 'active', 'booking', 'completed'
    
    # Relationships
    client = db.relationship('Client', backref='threads')
    messages = db.relationship('Message', backref='thread', lazy=True)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('message_thread.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_from_client = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        direction = "Client" if self.is_from_client else "Beautician"
        return f"<Message from {direction}: {self.content[:20]}...>"


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), nullable=False)
    business_hours = db.Column(db.Text)  # Stored as JSON
    auto_reply_enabled = db.Column(db.Boolean, default=True)
    default_appointment_duration = db.Column(db.Integer, default=60)  # minutes

    def get_business_hours(self):
        if self.business_hours:
            return json.loads(self.business_hours)
        return {}

    def set_business_hours(self, hours_dict):
        self.business_hours = json.dumps(hours_dict)


class PortfolioCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 'nails', 'eyelashes', 'eyebrows'
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Relationships
    items = db.relationship('PortfolioItem', backref='category', lazy=True)

    def __repr__(self):
        return f"<PortfolioCategory: {self.display_name}>"


class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('portfolio_category.id'), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    media_type = db.Column(db.String(20), nullable=False)  # 'image' or 'video'
    media_url = db.Column(db.String(500), nullable=False)  # URL or path to the media file
    thumbnail_url = db.Column(db.String(500))  # For videos, a thumbnail image
    is_featured = db.Column(db.Boolean, default=False)  # Featured items show on homepage
    display_order = db.Column(db.Integer, default=0)  # For ordering items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PortfolioItem: {self.title} ({self.media_type})>"


class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)  # 1-5 stars
    service_type = db.Column(db.String(100))  # Which service they had
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Testimonial from {self.client_name}>"
