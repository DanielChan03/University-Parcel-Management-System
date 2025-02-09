from flask import Blueprint, render_template, session, flash, redirect, url_for, request, jsonify
from datetime import datetime
from datetime import date
from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_
from flask_login import current_user, login_required
from .models import Courier, Parcel, ParcelStatus, Delivery,StudentStaff,University, db
from werkzeug.security import generate_password_hash
import random

courier = Blueprint('courier', __name__)

# Courier Dashboard
@courier.route('/courier-dashboard')
@login_required
def courier_dashboard():

    # Fetch active deliveries
    # Fetch active deliveries for today
    active_delivery = Delivery.query.filter(
        and_(
            Delivery.Courier_ID == current_user.Courier_ID,
            func.date(Delivery.Deliver_Date) == date.today()  # Filter only today's deliveries
        )
    ).order_by(Delivery.Deliver_Date.desc()).first()

    # Fetch collected parcels count
    collected_parcels = (
        Parcel.query.join(Delivery)
        .filter(
            Delivery.Courier_ID == current_user.Courier_ID,
            func.date(Delivery.Deliver_Date) == date.today()  # Filter parcels collected today
        )
        .count()
    )
    # Fetch reported parcels
    reported_issues = (
        ParcelStatus.query
        .join(Parcel, ParcelStatus.Parcel_ID == Parcel.Parcel_ID)
        .join(Delivery, Parcel.Delivery_ID == Delivery.Delivery_ID)
        .filter(
            Delivery.Courier_ID == current_user.Courier_ID,  # Filter by this courier's deliveries
            ParcelStatus.Status_Type.like("Reported -%")     # Status starts with "Reported -"
        )
        .count()
    )
     # Fetch the most recent delivery for the courier on or near today's date
    recent_delivery = Delivery.query.filter_by(Courier_ID=current_user.Courier_ID)\
        .filter(func.date(Delivery.Deliver_Date) <= date.today())\
        .order_by(Delivery.Deliver_Date.desc()).first()  # Get the most recent delivery

    if recent_delivery:
        # Now, use the Delivery ID to find parcels related to this delivery
        parcels_for_delivery = Parcel.query.filter_by(Delivery_ID=recent_delivery.Delivery_ID).all()

        if parcels_for_delivery:
            # Track the recipient's university destination for the first parcel (or adjust as needed)
            parcel = parcels_for_delivery[0]  # You can also iterate if multiple parcels are involved
            recipient = StudentStaff.query.filter_by(User_ID=parcel.Recipient_User_ID).first()

            if recipient:
                university = University.query.filter_by(University_ID=recipient.University_ID).first()
                destination = university.University_Name if university else 'University Not Found'
            else:
                destination = 'Recipient information not found'
        else:
            destination = "No parcels found for this delivery"
    else:
        destination = "No deliveries found for today"

    # Fetch nearest scheduled delivery (future only)
    scheduled_delivery = Delivery.query.filter(
        and_(
            Delivery.Courier_ID == current_user.Courier_ID,
            Delivery.Deliver_Date > date.today()

        )
    ).order_by(Delivery.Deliver_Date.asc()).first()

    # Determine delivery messages
    if active_delivery:
        today_delivery_message = f"You have a Delivery {active_delivery.Delivery_ID} Today"
    else:
        today_delivery_message = "No Delivery Today"
    
    if scheduled_delivery:
        future_delivery_message = f"Delivery {scheduled_delivery.Delivery_ID} is Scheduled at {scheduled_delivery.Deliver_Date}"
    else:
        future_delivery_message = "No Future Task"

    return render_template(
        "Courier/CourierDashboard.html",
        courier=current_user,
        active_delivery_id=active_delivery.Delivery_ID if active_delivery else "None",
        active_delivery_date=active_delivery.Deliver_Date if active_delivery else "N/A",
        collected_parcels=collected_parcels,
        reported_issues=reported_issues,
        destination=destination,
        today_delivery_message=today_delivery_message,
        future_delivery_message=future_delivery_message
    )

# View Assigned Parcels
@courier.route('/assigned-parcels', methods=['GET'])
@login_required
def view_assigned_parcels():
    assigned_parcels = Parcel.query.filter_by(Delivery_ID=current_user.Courier_ID).all()
    return render_template("Courier/CourierAssignedParcels.html", parcels=assigned_parcels)

# Report Parcel
from flask import redirect, url_for

@courier.route('/report-parcel', methods=['GET', 'POST'])
@login_required
def report_parcel():
    if request.method == 'POST':
        parcel_id = request.form.get("parcel_id")
        issue_description = request.form.get("issue_description")
        issue_type = request.form.get("issue_type")
        other_description = request.form.get("other_description") 
        
        if not parcel_id or not issue_description:
            flash("Parcel ID and issue description are required.", "danger")
            return render_template("Courier/CourierReportDelivery.html")

        # Check if the parcel exists
        parcel = Parcel.query.filter_by(Parcel_ID=parcel_id).first()
        if not parcel:
            flash("Parcel ID not found. Please enter a valid Parcel ID.", "danger")
            return render_template("Courier/CourierReportDelivery.html")

        # Generate the base issue type
        if issue_type == "other" and other_description:
            status_type = f"Reported - {other_description}"  # For "Other", use the custom description
        else:
            status_type = f"Reported - {issue_type.capitalize()} Parcel"  # For regular issue types

         # Generate a unique Status_ID
        new_status_id = f"REP{random.randint(100000, 999999)}"
        while db.session.query(ParcelStatus).filter_by(Status_ID=new_status_id).first():
            new_status_id = f"REP{random.randint(100000, 999999)}"  # Regenerate until unique

        # Create a new report
        new_report = ParcelStatus(
            Status_ID=new_status_id,
            Parcel_ID=parcel_id,
            Status_Type=status_type,
            Updated_by=current_user.Courier_ID,
            Updated_At=datetime.now()
        )
        db.session.add(new_report)
        db.session.commit()

        flash("Parcel issue reported successfully!", "success")
        return redirect(url_for('courier.report_parcel'))  # Redirect to avoid resubmission

    return render_template("Courier/CourierReportDelivery.html")

# Initialize notifications in the session if not already present
def init_notifications():
    if 'notifications' not in session:
        session['notifications'] = []

# Add a notification to the session
def add_notification(recipient_id, title, message):
    init_notifications()
    notification = {
        'id': f"NOT{random.randint(100000, 999999)}",  # Generate a unique ID
        'recipient_id': recipient_id,
        'title': title,
        'message': message,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': False
    }
    session['notifications'].append(notification)
    session.modified = True  # Ensure the session is marked as modified

# Get notifications for the current user
def get_notifications(recipient_id):
    init_notifications()
    return [n for n in session['notifications'] if n['recipient_id'] == recipient_id]

# Mark a notification as read
def mark_notification_read(notification_id):
    init_notifications()
    for notification in session['notifications']:
        if notification['id'] == notification_id:
            notification['is_read'] = True
            session.modified = True
            break

# Render the CourierNotifications.html page
@courier.route('/notifications', methods=['GET'])
@login_required
def notifications_page():
    
    return render_template("Courier/CourierNotifications.html")

# Send Notification
@courier.route('/send-notification', methods=['POST'])
@login_required
def send_notification():
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    title = data.get('title')
    message = data.get('message')

    if not recipient_id or not title or not message:
        return jsonify({'success': False, 'message': 'Missing required fields.'}), 400

    # Add the notification to the session
    add_notification(recipient_id, title, message)

    return jsonify({'success': True, 'message': 'Notification sent successfully.'})

# Get Notifications
@courier.route('/get-notifications', methods=['GET'])
@login_required
def get_notifications_route():
    # Fetch notifications for the current user
    notifications = get_notifications(current_user.get_id())

    return jsonify({'success': True, 'notifications': notifications})

# Mark Notification as Read
@courier.route('/mark-notification-read/<string:notification_id>', methods=['POST'])
@login_required
def mark_notification_read_route(notification_id):
    mark_notification_read(notification_id)
    return jsonify({'success': True, 'message': 'Notification marked as read.'})

# Collect parcel
@courier.route('/collect-parcel', methods=['GET', 'POST'])
@login_required
def collect_parcel():
    if request.method == 'POST':
        # Handle POST request to update parcel status
        data = request.get_json()
        collected_parcels = data.get('collectedParcels', [])
        uncollected_parcels = data.get('uncollectedParcels', [])

        # Handle collected parcels (Ready to Pickup to Parcel Collected)
        for parcel_id in collected_parcels:
            # Check the latest status of the parcel
            latest_status = ParcelStatus.query.filter_by(Parcel_ID=parcel_id).order_by(ParcelStatus.Updated_At.desc()).first()
            if latest_status and latest_status.Status_Type != 'Parcel Collected':
                # Generate a unique status ID
                new_status_id = f"COL{random.randint(100000, 999999)}"
                while db.session.query(ParcelStatus).filter_by(Status_ID=new_status_id).first():
                    new_status_id = f"COL{random.randint(100000, 999999)}"  # Regenerate until unique

                # Create a new status entry for Parcel Collected
                new_status_entry = ParcelStatus(
                    Status_ID=new_status_id,
                    Parcel_ID=parcel_id,
                    Status_Type='Parcel Collected',
                    Updated_by=current_user.Courier_ID,
                    Updated_At=datetime.now()
                )
                db.session.add(new_status_entry)

        # Handle uncollected parcels (Parcel Collected to Ready to Pickup)
        for parcel_id in uncollected_parcels:
            # Check if the current status is "Parcel Collected"
            latest_status = ParcelStatus.query.filter_by(Parcel_ID=parcel_id).order_by(ParcelStatus.Updated_At.desc()).first()
            if latest_status and latest_status.Status_Type == 'Parcel Collected':
                # Generate a unique status ID for Ready to Pickup
                new_status_id = f"COL{random.randint(100000, 999999)}"
                while db.session.query(ParcelStatus).filter_by(Status_ID=new_status_id).first():
                    new_status_id = f"COL{random.randint(100000, 999999)}"  # Regenerate until unique

                # Create a new status entry for Ready to Pickup
                new_status_entry = ParcelStatus(
                    Status_ID=new_status_id,
                    Parcel_ID=parcel_id,
                    Status_Type='Ready to Pickup',
                    Updated_by=current_user.Courier_ID,
                    Updated_At=datetime.now()
                )
                db.session.add(new_status_entry)

        db.session.commit()  # Commit all status updates
        return jsonify({'success': True})

    # Handle GET request to render the page
    search_date = request.args.get('searchDate')  # Get searchDate from query parameters

    if search_date:
        # Convert the string to a date object
        search_date = datetime.strptime(search_date, '%Y-%m-%d').date()

        deliveries = Delivery.query.filter(
            func.date(Delivery.Deliver_Date) == search_date,
            Delivery.Courier_ID == current_user.Courier_ID
            ).all()
        
        if not deliveries:
            return jsonify({'message': 'No deliveries found for this date'})
        
    else:
        # Query deliveries for the current courier until today (default if no searchDate is provided)
        deliveries = Delivery.query.filter_by(Courier_ID=current_user.Courier_ID)\
            .filter(Delivery.Deliver_Date <= date.today())\
            .order_by(Delivery.Deliver_Date.desc()).all()  # Get all deliveries until today

    # Prepare the data for the frontend
    delivery_data = []
    for delivery in deliveries:
        # Query the parcels associated with each delivery
        parcels = Parcel.query.filter_by(Delivery_ID=delivery.Delivery_ID).order_by(Parcel.Parcel_ID.asc()).all()

        parcel_data = []
        for parcel in parcels:
            # Get the most recent status for the parcel
            latest_status = ParcelStatus.query.filter_by(Parcel_ID=parcel.Parcel_ID).order_by(ParcelStatus.Updated_At.desc()).first()

            # If a status update exists, use it; otherwise, use 'Not Updated'
            status = latest_status.Status_Type if latest_status else 'Not Updated'

            # Get recipient details
            recipient = StudentStaff.query.filter_by(User_ID=parcel.Recipient_User_ID).first()
            if recipient:
                university = University.query.filter_by(University_ID=recipient.University_ID).first()
                destination = university.University_Name if university else 'University Not Found'
            else:
                destination = 'Recipient information not found'

            parcel_data.append({
                'Parcel_ID': parcel.Parcel_ID,
                'Sender': parcel.sender.User_Name,
                'Recipient': recipient.User_Name if recipient else 'Unknown',
                'Destination': destination,
                'Status': status,
            })

        # Append the parcel data to the respective delivery
        delivery_data.append({
            'Delivery_ID': delivery.Delivery_ID,
            'Delivery_Date': delivery.Deliver_Date,
            'Parcels': parcel_data
        })

    # Return JSON for AJAX requests
    if request.args.get('searchDate'):
        return jsonify({'deliveries': delivery_data})
    else:
        return render_template("Courier/CourierCollectParcel.html", deliveries=delivery_data)

#View Parcel Manager List
@courier.route('/view-managers',methods =['GET'])
@login_required
def courierViewManagerList():

     # Get the currently logged-in courier's ID
    current_courier_id = current_user.get_id()  # Assuming `current_user` is the logged-in courier


    deliveries = Delivery.query.filter_by(Courier_ID=current_courier_id).all()
    delivery_ids = [delivery.Delivery_ID for delivery in deliveries]

    # Query the Parcel table and join with ParcelManager for Send and Receive Managers
    parcels = Parcel.query.options(
        joinedload(Parcel.send_manager),  # Eager load the send manager
        joinedload(Parcel.receive_manager)  # Eager load the receive manager
    ).filter(Parcel.Delivery_ID.in_(delivery_ids)).order_by(Parcel.Parcel_ID.asc()).all()

    # Prepare the data to pass to the template
    parcel_data = []
    for parcel in parcels:
        parcel_info = {
            'Parcel_ID': parcel.Parcel_ID,
            'Send_Manager_ID': parcel.Send_Manager_ID,
            'Send_Manager_Name': parcel.send_manager.Manager_Name if parcel.send_manager else 'N/A',
            'Send_Manager_Email': parcel.send_manager.Manager_Email if parcel.send_manager else 'N/A',
            'Send_Manager_Contact': parcel.send_manager.Manager_Contact if parcel.send_manager else 'N/A',
            'Send_Manager_Branch': parcel.send_manager.Manager_Work_Branch if parcel.send_manager else 'N/A',
            'Receive_Manager_ID': parcel.Receive_Manager_ID,
            'Receive_Manager_Name': parcel.receive_manager.Manager_Name if parcel.receive_manager else 'N/A',
            'Receive_Manager_Email': parcel.receive_manager.Manager_Email if parcel.receive_manager else 'N/A',
            'Receive_Manager_Contact': parcel.receive_manager.Manager_Contact if parcel.receive_manager else 'N/A',
            'Receive_Manager_Branch': parcel.receive_manager.Manager_Work_Branch if parcel.receive_manager else 'N/A',
        }
        parcel_data.append(parcel_info)
    
    return render_template('Courier/CourierViewManagerList.html',parcels = parcel_data)
