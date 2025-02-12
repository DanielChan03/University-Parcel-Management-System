from flask import Blueprint, render_template, session
from datetime import date
from sqlalchemy import func, and_
from flask_login import current_user, login_required
from webapp.models import Delivery, Parcel, ParcelStatus, StudentStaff, University, db
from webapp.Couriercode.notifications import init_notifications
courier_dashboard_bp = Blueprint('courier_dashboard', __name__)
# Courier Dashboard
@courier_dashboard_bp.route('/courier-dashboard')
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
        today_delivery_message = f"You have a Delivery {active_delivery.Delivery_ID} today"
    else:
        today_delivery_message = "No Delivery today"
    
    if scheduled_delivery:
        future_delivery_message = f"Delivery {scheduled_delivery.Delivery_ID} is scheduled at {scheduled_delivery.Deliver_Date}"
    else:
        future_delivery_message = "No Future Task"

       # Count messages sent and received by the current user
    current_user_email = current_user.Courier_Email
    messages_sent = count_messages_sent(current_user_email)
    messages_received = count_messages_received(current_user_email)

    return render_template(
        "Courier/CourierDashboard.html",
        courier=current_user,
        active_delivery_id=active_delivery.Delivery_ID if active_delivery else "None",
        active_delivery_date=active_delivery.Deliver_Date if active_delivery else "N/A",
        collected_parcels=collected_parcels,
        reported_issues=reported_issues,
        destination=destination,
        today_delivery_message=today_delivery_message,
        future_delivery_message=future_delivery_message,
        messages_sent=messages_sent,
        messages_received=messages_received
    )

def count_messages_sent(current_user_email):
    init_notifications()  # Ensure notifications are initialized

    # Check if 'notifications' exists and is a list
    if 'notifications' not in session or not isinstance(session['notifications'], list):
        return 0  # Return 0 if the key is missing or not a list

    return sum(1 for n in session['notifications'] if 'sender_email' in n and n['sender_email'] == current_user_email)

def count_messages_received(current_user_email):
    init_notifications()

    if 'notifications' not in session or not isinstance(session['notifications'], list):
        return 0

    return sum(1 for n in session['notifications'] if 'recipient_email' in n and n['recipient_email'] == current_user_email)
