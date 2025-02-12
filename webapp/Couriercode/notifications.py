from flask import Blueprint,render_template, jsonify, request, session
from datetime import datetime
from webapp.models import Courier, StudentStaff, ParcelManager
from flask_login import current_user, login_required
import random

notifications_bp = Blueprint('notifications', __name__)

# Initialize notifications in the session if not already present
def init_notifications():
    if 'notifications' not in session:
        session['notifications'] = []

def is_valid_recipient(email):
    # Check if the email exists in any of the user tables.
    return (
        StudentStaff.query.filter_by(User_Email=email).first() or
        ParcelManager.query.filter_by(Manager_Email=email).first() or
        Courier.query.filter_by(Courier_Email=email).first()
    )

# Add a notification to the session
def add_notification(recipient_email, title, message, sender_email):
    init_notifications()

    if not is_valid_recipient(recipient_email):
        return {'success': False, 'message': 'Recipient email not found.'}  # Don't add if recipient doesn't exist


    notification = {
        'id': f"NOT{random.randint(100000, 999999)}",  # Generate a unique ID
        'recipient_email': recipient_email,
        'title': title,
        'message': message,
        'sender_email': sender_email, 
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': False
    }
    session['notifications'].append(notification)
    session.modified = True  # Ensure the session is marked as modified
    return {'success': True, 'message': 'Message Succesfully sent'} 

# Get notifications for the current user
@notifications_bp.route('/get-notification/<string:notification_id>', methods=['GET'])
@login_required
def get_notifications_by_id(notification_id):
    init_notifications()
    notification = next((n for n in session['notifications'] if n['id'] == notification_id), None)
    if notification:
        return jsonify({'success': True, 'notification': notification})
    else:
        return jsonify({'success': False, 'message': 'Notification not found.'}), 404
    
@notifications_bp.route('/reply-notification/<string:notification_id>', methods=['POST'])
@login_required
def reply_notification(notification_id):
    data = request.get_json()
    reply_message = data.get('reply_message')

    if not reply_message:
        return jsonify({'success': False, 'message': 'Reply message is required.'}), 400

    # Fetch the original notification
    init_notifications()
    original_notification = next((n for n in session['notifications'] if n['id'] == notification_id), None)
    if not original_notification:
        return jsonify({'success': False, 'message': 'Notification not found.'}), 404

    # Get the sender's email (e.g., current user's email)
    sender_email = current_user.Courier_Email  # Assuming the current user has an email field

    # Send the reply as a new notification to the original sender
    add_notification(original_notification['sender_email'], 'Reply to your notification', reply_message, sender_email)
    return jsonify({'success': True, 'message': 'Reply sent successfully.'})

# Mark a notification as read
def mark_notification_read(notification_id):
    init_notifications()
    for notification in session['notifications']:
        if notification['id'] == notification_id:
            notification['is_read'] = True
            session.modified = True
            break

# Render the CourierNotifications.html page
@notifications_bp.route('/notifications', methods=['GET'])
@login_required
def notifications_page():
    notifications = get_notifications_by_id(current_user.get_id())
    return render_template("Courier/CourierNotifications.html", notifications=notifications)

# Send Notification
@notifications_bp.route('/send-notification', methods=['POST'])
@login_required
def send_notification():
    data = request.get_json()
    recipient_email = data.get('recipient_email')
    title = data.get('title')
    message = data.get('message')

    if not recipient_email or not title or not message:
        return jsonify({'success': False, 'message': 'Missing required fields.'}), 400

    # Determine the sender's email based on the current user's role
    sender_email = current_user.Courier_Email

    # Add the notification to the session
    result = add_notification(recipient_email, title, message, sender_email)

    return jsonify(result)

# Get Notifications
@notifications_bp.route('/get-notifications', methods=['GET'])
@login_required
def get_notifications_route():
    # Fetch notifications for the current user
    init_notifications()

    # Get the current user's email
    recipient_email = getattr(current_user, 'Courier_Email', None)

    if not recipient_email:
        return jsonify({'success': False, 'message': 'User email not found.'}), 400
     # Ensure session['notifications'] is a list before filtering
    notifications = session.get('notifications', [])

    # Filter notifications for the current recipient
    user_notifications = [n for n in notifications if n.get('recipient_email') == recipient_email]

    return jsonify({'success': True, 'notifications': user_notifications})

# Mark Notification as Read
@notifications_bp.route('/mark-notification-read/<string:notification_id>', methods=['POST'])
@login_required
def mark_notification_read_route(notification_id):
    init_notifications()  # Ensure notifications are initialized
    
    if 'read_notifications' not in session:
        session['read_notifications'] = []  # Use a list instead of a set

    notification = next((n for n in session['notifications'] if n['id'] == notification_id), None)

    if not notification:
        return jsonify({'success': False, 'message': 'Notification not found.'}), 404

    # Ensure only the recipient can mark it as read
    if notification['recipient_email'] != current_user.Courier_Email:
        return jsonify({'success': False, 'message': 'You are not allowed to mark this notification as read.'}), 403

    # Store read notification ID in session
    if notification_id not in session['read_notifications']:
        session['read_notifications'].append(notification_id)  
        session.modified = True  # Ensure session is saved

    notification['is_read'] = True  # Mark as read

    return jsonify({'success': True, 'message': 'Notification marked as read.'})
