from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
import json
import logging
import datetime
from app import app, db
from models import User, Client, TimeSlot, Appointment, Service, Settings, MessageThread, Message
from facebook_messenger import FacebookMessenger
from instagram_api import InstagramAPI
from messaging import MessageHandler
from werkzeug.security import generate_password_hash, check_password_hash

# Add function to add current datetime to templates
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now}

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize message handling
fb_messenger = FacebookMessenger()
instagram_api = InstagramAPI()
message_handler = MessageHandler()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Debug logging - use print for better visibility
        print(f"=== Login attempt for email: {email} ===")
        
        # Try finding user by email first
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # If no user by email, try by username
            user = User.query.filter_by(username=email).first()
            print(f"No user found by email, trying username lookup: {user is not None}")
        
        if user:
            print(f"User found: ID={user.id}, Username={user.username}")
            print(f"Password hash exists: {user.password_hash is not None}")
            
            try:
                password_check = user.check_password(password)
                print(f"Password check result: {password_check}")
                
                if password_check:
                    login_user(user)
                    print(f"User logged in successfully: {user.username}")
                    return redirect(url_for('dashboard'))
                else:
                    print("Password verification failed")
                    flash('Invalid email or password', 'danger')
            except Exception as e:
                print(f"Error checking password: {str(e)}")
                flash('An error occurred during login', 'danger')
        else:
            print("No user found with this email or username")
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get today's date
    today = datetime.date.today()
    
    # Get today's appointments
    today_appointments = Appointment.query.filter_by(
        user_id=current_user.id,
        date=today,
        status='confirmed'
    ).order_by(Appointment.start_time).all()
    
    # Get upcoming appointments (next 7 days excluding today)
    next_week = today + datetime.timedelta(days=7)
    upcoming_appointments = Appointment.query.filter(
        Appointment.user_id == current_user.id,
        Appointment.date > today,
        Appointment.date <= next_week,
        Appointment.status == 'confirmed'
    ).order_by(Appointment.date, Appointment.start_time).all()
    
    # Get recent messages
    recent_threads = MessageThread.query.join(
        Message, MessageThread.id == Message.thread_id
    ).filter(
        MessageThread.status != 'completed'
    ).group_by(
        MessageThread.id
    ).order_by(
        MessageThread.last_message_at.desc()
    ).limit(5).all()
    
    recent_messages = []
    for thread in recent_threads:
        last_message = Message.query.filter_by(
            thread_id=thread.id
        ).order_by(
            Message.timestamp.desc()
        ).first()
        
        if last_message:
            client = Client.query.get(thread.client_id)
            recent_messages.append({
                'thread_id': thread.id,
                'client_name': client.name or 'Unknown Client',
                'message': last_message.content,
                'timestamp': last_message.timestamp,
                'is_from_client': last_message.is_from_client,
                'platform': thread.platform
            })
    
    # Get availability for the next 7 days
    availability = []
    for i in range(7):
        day = today + datetime.timedelta(days=i)
        time_slots = TimeSlot.query.filter_by(
            user_id=current_user.id,
            date=day,
            is_available=True
        ).all()
        
        availability.append({
            'date': day,
            'slots': len(time_slots)
        })
    
    return render_template(
        'dashboard.html',
        today_appointments=today_appointments,
        upcoming_appointments=upcoming_appointments,
        recent_messages=recent_messages,
        availability=availability
    )

@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    if request.method == 'POST':
        data = request.get_json()
        
        if data and 'action' in data:
            if data['action'] == 'add_slot':
                try:
                    date_str = data.get('date')
                    start_time_str = data.get('start_time')
                    end_time_str = data.get('end_time')
                    
                    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
                    end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()
                    
                    # Create new time slot
                    time_slot = TimeSlot(
                        user_id=current_user.id,
                        date=date,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True
                    )
                    
                    db.session.add(time_slot)
                    db.session.commit()
                    
                    return jsonify({'success': True, 'message': 'Time slot added'})
                except Exception as e:
                    logger.error(f"Error adding time slot: {str(e)}")
                    return jsonify({'success': False, 'message': str(e)})
            
            elif data['action'] == 'remove_slot':
                try:
                    slot_id = data.get('slot_id')
                    
                    time_slot = TimeSlot.query.get(slot_id)
                    if time_slot and time_slot.user_id == current_user.id:
                        db.session.delete(time_slot)
                        db.session.commit()
                        
                        return jsonify({'success': True, 'message': 'Time slot removed'})
                    else:
                        return jsonify({'success': False, 'message': 'Time slot not found'})
                except Exception as e:
                    logger.error(f"Error removing time slot: {str(e)}")
                    return jsonify({'success': False, 'message': str(e)})
            
            elif data['action'] == 'update_slot':
                try:
                    slot_id = data.get('slot_id')
                    is_available = data.get('is_available', True)
                    
                    time_slot = TimeSlot.query.get(slot_id)
                    if time_slot and time_slot.user_id == current_user.id:
                        time_slot.is_available = is_available
                        db.session.commit()
                        
                        return jsonify({'success': True, 'message': 'Time slot updated'})
                    else:
                        return jsonify({'success': False, 'message': 'Time slot not found'})
                except Exception as e:
                    logger.error(f"Error updating time slot: {str(e)}")
                    return jsonify({'success': False, 'message': str(e)})
        
        return jsonify({'success': False, 'message': 'Invalid request'})
    
    # Get the requested date or default to today
    date_str = request.args.get('date', datetime.date.today().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.date.today()
    
    # Get time slots for the selected date
    time_slots = TimeSlot.query.filter_by(
        user_id=current_user.id,
        date=selected_date
    ).order_by(TimeSlot.start_time).all()
    
    # Get appointments for the selected date
    appointments = Appointment.query.filter_by(
        user_id=current_user.id,
        date=selected_date
    ).order_by(Appointment.start_time).all()
    
    # Generate a week view
    week_dates = []
    start_of_week = selected_date - datetime.timedelta(days=selected_date.weekday())
    for i in range(7):
        day_date = start_of_week + datetime.timedelta(days=i)
        week_dates.append(day_date)
    
    return render_template(
        'schedule.html',
        selected_date=selected_date,
        time_slots=time_slots,
        appointments=appointments,
        week_dates=week_dates
    )

@app.route('/appointments')
@login_required
def appointments():
    # Get filter parameters
    status = request.args.get('status', 'all')
    date_from_str = request.args.get('date_from', '')
    date_to_str = request.args.get('date_to', '')
    
    # Query base
    query = Appointment.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if status != 'all':
        query = query.filter_by(status=status)
    
    if date_from_str:
        try:
            date_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
            query = query.filter(Appointment.date >= date_from)
        except ValueError:
            pass
    
    if date_to_str:
        try:
            date_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()
            query = query.filter(Appointment.date <= date_to)
        except ValueError:
            pass
    
    # Order by date and time
    appointments = query.order_by(Appointment.date.desc(), Appointment.start_time).all()
    
    return render_template(
        'appointments.html',
        appointments=appointments,
        status=status,
        date_from=date_from_str,
        date_to=date_to_str
    )

@app.route('/appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def appointment_detail(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Ensure the appointment belongs to the current user
    if appointment.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update':
            appointment.status = request.form.get('status')
            appointment.notes = request.form.get('notes')
            db.session.commit()
            flash('Appointment updated successfully', 'success')
        
        elif action == 'cancel':
            appointment.status = 'cancelled'
            db.session.commit()
            flash('Appointment cancelled successfully', 'success')
        
        elif action == 'complete':
            appointment.status = 'completed'
            db.session.commit()
            flash('Appointment marked as completed', 'success')
        
        return redirect(url_for('appointment_detail', appointment_id=appointment_id))
    
    return render_template('appointment_detail.html', appointment=appointment)

@app.route('/clients')
@login_required
def clients():
    # Get all clients with appointments for the current user
    clients = Client.query.join(
        Appointment, Client.id == Appointment.client_id
    ).filter(
        Appointment.user_id == current_user.id
    ).distinct().all()
    
    return render_template('clients.html', clients=clients)

@app.route('/client/<int:client_id>')
@login_required
def client_detail(client_id):
    client = Client.query.get_or_404(client_id)
    
    # Get all appointments for this client with the current user
    appointments = Appointment.query.filter_by(
        user_id=current_user.id,
        client_id=client_id
    ).order_by(Appointment.date.desc(), Appointment.start_time).all()
    
    # Get messages for this client
    threads = MessageThread.query.filter_by(client_id=client_id).all()
    messages = []
    
    for thread in threads:
        thread_messages = Message.query.filter_by(thread_id=thread.id).order_by(Message.timestamp).all()
        messages.extend(thread_messages)
    
    # Sort messages by timestamp
    messages.sort(key=lambda x: x.timestamp)
    
    return render_template(
        'client_detail.html',
        client=client,
        appointments=appointments,
        messages=messages
    )

@app.route('/messages')
@login_required
def messages():
    # Get all message threads
    threads = MessageThread.query.order_by(MessageThread.last_message_at.desc()).all()
    
    # Prepare data for template
    thread_data = []
    for thread in threads:
        client = Client.query.get(thread.client_id)
        last_message = Message.query.filter_by(thread_id=thread.id).order_by(Message.timestamp.desc()).first()
        
        if client and last_message:
            thread_data.append({
                'id': thread.id,
                'client': client,
                'last_message': last_message,
                'platform': thread.platform,
                'status': thread.status
            })
    
    return render_template('messages.html', threads=thread_data)

@app.route('/message/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def message_detail(thread_id):
    thread = MessageThread.query.get_or_404(thread_id)
    client = Client.query.get(thread.client_id)
    
    if request.method == 'POST':
        message_text = request.form.get('message')
        
        if message_text:
            # Create new message
            message = Message(
                thread_id=thread.id,
                content=message_text,
                is_from_client=False
            )
            db.session.add(message)
            
            # Update thread last message time
            thread.last_message_at = datetime.datetime.utcnow()
            db.session.commit()
            
            # Send message via appropriate platform
            if thread.platform == 'messenger' and client.messenger_id:
                fb_messenger.send_message(client.messenger_id, message_text)
            elif thread.platform == 'instagram' and client.instagram_id:
                instagram_api.send_direct_message(client.instagram_id, message_text)
            
            flash('Message sent successfully', 'success')
            return redirect(url_for('message_detail', thread_id=thread_id))
    
    # Get all messages for this thread
    messages = Message.query.filter_by(thread_id=thread.id).order_by(Message.timestamp).all()
    
    return render_template(
        'message_detail.html',
        thread=thread,
        client=client,
        messages=messages
    )

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Get user settings or create if not exists
    settings = Settings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        settings = Settings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            current_user.business_name = request.form.get('business_name')
            current_user.phone = request.form.get('phone')
            current_user.email = request.form.get('email')
            
            # Update password if provided
            password = request.form.get('password')
            if password:
                current_user.set_password(password)
            
            db.session.commit()
            flash('Profile updated successfully', 'success')
        
        elif action == 'update_settings':
            settings.auto_reply_enabled = 'auto_reply' in request.form
            settings.default_appointment_duration = int(request.form.get('appointment_duration', 60))
            
            # Update business hours
            business_hours = {}
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for day in days:
                start_time = request.form.get(f'{day.lower()}_start')
                end_time = request.form.get(f'{day.lower()}_end')
                
                if start_time and end_time:
                    business_hours[day] = {
                        'start': start_time,
                        'end': end_time
                    }
                else:
                    business_hours[day] = {
                        'start': None,
                        'end': None
                    }
            
            settings.set_business_hours(business_hours)
            db.session.commit()
            
            flash('Settings updated successfully', 'success')
        
        return redirect(url_for('settings'))
    
    return render_template('settings.html', settings=settings)

@app.route('/fb-webhook', methods=['GET', 'POST'])
def fb_webhook():
    if request.method == 'GET':
        # Facebook webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if fb_messenger.verify_webhook(mode, token):
            return challenge
        
        return 'Verification failed', 403
    
    elif request.method == 'POST':
        # Process incoming webhook data
        data = request.json
        messages = fb_messenger.process_webhook(data)
        
        for msg in messages:
            user = User.query.first()  # In MVP, we're assuming a single user
            if user:
                message_handler.process_message(
                    msg['sender_id'],
                    msg['message'],
                    'messenger',
                    user.id
                )
        
        return 'EVENT_RECEIVED'

@app.route('/ig-webhook', methods=['GET', 'POST'])
def ig_webhook():
    if request.method == 'GET':
        # Instagram webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # For simplicity, using the same verification mechanism as Facebook
        if fb_messenger.verify_webhook(mode, token):
            return challenge
        
        return 'Verification failed', 403
    
    elif request.method == 'POST':
        # Process incoming webhook data
        data = request.json
        messages = instagram_api.process_webhook(data)
        
        for msg in messages:
            user = User.query.first()  # In MVP, we're assuming a single user
            if user:
                message_handler.process_message(
                    msg['sender_id'],
                    msg['message'],
                    'instagram',
                    user.id
                )
        
        return 'EVENT_RECEIVED'

@app.route('/calendar')
@login_required
def calendar():
    # This route provides data for the full calendar view
    return render_template('calendar.html')

@app.route('/api/calendar-events')
@login_required
def calendar_events():
    # Get date range from request (if provided)
    start_date_str = request.args.get('start')
    end_date_str = request.args.get('end')
    
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    except ValueError:
        # If dates are invalid, use a default range
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=30)
        end_date = today + datetime.timedelta(days=60)
    
    # Query for appointments in the date range
    query = Appointment.query.filter_by(user_id=current_user.id)
    
    if start_date:
        query = query.filter(Appointment.date >= start_date)
    if end_date:
        query = query.filter(Appointment.date <= end_date)
    
    appointments = query.all()
    
    # Query for available time slots in the date range
    slot_query = TimeSlot.query.filter_by(
        user_id=current_user.id,
        is_available=True
    )
    
    if start_date:
        slot_query = slot_query.filter(TimeSlot.date >= start_date)
    if end_date:
        slot_query = slot_query.filter(TimeSlot.date <= end_date)
    
    time_slots = slot_query.all()
    
    # Format data for FullCalendar
    events = []
    
    for appointment in appointments:
        client_name = "Unnamed Client"
        if appointment.client:
            client_name = appointment.client.name or "Unnamed Client"
        
        start_datetime = datetime.datetime.combine(appointment.date, appointment.start_time)
        end_datetime = datetime.datetime.combine(appointment.date, appointment.end_time)
        
        color = "#28a745"  # success/green for confirmed
        if appointment.status == 'cancelled':
            color = "#dc3545"  # danger/red
        elif appointment.status == 'completed':
            color = "#17a2b8"  # info/blue
        
        events.append({
            'id': f'appointment-{appointment.id}',
            'title': f'{client_name} - {appointment.service_type or "Nail Service"}',
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'type': 'appointment',
                'appointmentId': appointment.id,
                'clientName': client_name,
                'status': appointment.status
            }
        })
    
    for slot in time_slots:
        start_datetime = datetime.datetime.combine(slot.date, slot.start_time)
        end_datetime = datetime.datetime.combine(slot.date, slot.end_time)
        
        events.append({
            'id': f'slot-{slot.id}',
            'title': 'Available',
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'backgroundColor': '#6c757d',  # secondary/gray
            'borderColor': '#6c757d',
            'extendedProps': {
                'type': 'slot',
                'slotId': slot.id
            }
        })
    
    return jsonify(events)

# Create a user route for initial setup
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    # Check if there are any users
    user_count = User.query.count()
    
    if user_count > 0:
        flash('Setup has already been completed', 'info')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        business_name = request.form.get('business_name')
        
        # Create initial user
        user = User(username=username, email=email, business_name=business_name)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create default settings
        settings = Settings(user_id=user.id)
        db.session.add(settings)
        db.session.commit()
        
        flash('Setup completed successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('setup.html')
