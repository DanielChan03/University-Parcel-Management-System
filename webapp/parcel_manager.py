from flask import Blueprint, render_template, session, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from .models import  Parcel, ParcelStatus, Waitlist, ParcelManager, Courier, SmartLocker, db
from werkzeug.security import generate_password_hash
import random

parcel_manager = Blueprint('parcel_manager', __name__)

# Parcel Manager Dashboard
@parcel_manager.route('/parcel-manager-dashboard')
@login_required
def parcel_manager_dashboard():
    if not isinstance(current_user, ParcelManager):
        flash('Unauthorized access! Please log in as a Parcel Manager.', category="error")
        return redirect(url_for('parcel_manager_auth.parcel_manager_login'))

    # Fetch notifications (unresponded feedback) from session
    notifications = session.get('feedback', {})

    # Fetch parcel statistics
    total_received_parcels = Parcel.query.count()

    # Fetch delivered parcels (status type is "Delivered")
    total_delivered_parcels = db.session.query(ParcelStatus).filter_by(Status_Type='Delivered').count()

    # Fetch pending parcels (status type is not "Delivered")
    pending_parcels = db.session.query(ParcelStatus).filter(ParcelStatus.Status_Type != "Delivered").count()

    # Fetch locker status
    locker_status = db.session.query(SmartLocker.Locker_Status).all()

    return render_template(
        "ParcelManager/ParcelManagerDashboard.html",
        parcel_manager = current_user,
        notifications = notifications,
        total_received_parcels = total_received_parcels,
        total_delivered_parcels = total_delivered_parcels,
        pending_parcels = pending_parcels,
        locker_status = locker_status
    )

@parcel_manager.route('/assign_parcel_to_courier', methods=['GET', 'POST'])
def assign_parcel_to_courier():
    if request.method == 'POST':
        parcel_id = request.form.get('parcel_id')
        courier_id = request.form.get('courier_id')

        if not parcel_id or not courier_id:
            flash("Please select both a parcel and a courier!", "error")
            return redirect(url_for('parcel_manager.assign_parcel_to_courier'))

        parcel = Parcel.query.get(parcel_id)
        courier = Courier.query.get(courier_id)

        if parcel and courier:
            # Check if the parcel already has a delivery assigned
            if parcel.Delivery_ID:
                flash(f"Parcel {parcel_id} is already assigned!", "warning")
            else:
                # Create a new delivery record
                new_delivery = Delivery(
                    Delivery_ID=f"D_{parcel_id}",  # Unique delivery ID (Example format)
                    Courier_ID=courier.Courier_ID,  # Assign to selected courier
                    Deliver_Date=None,  # Delivery date not set yet
                    Arrival_Date=None   # Arrival date not set yet
                )
                db.session.add(new_delivery)
                db.session.commit()

                # Assign the delivery to the parcel
                parcel.Delivery_ID = new_delivery.Delivery_ID
                db.session.commit()

                flash(f"Parcel {parcel_id} assigned to Courier {courier.Courier_ID} successfully!", "success")
        else:
            flash("Invalid parcel or courier selected!", "error")

        return redirect(url_for('parcel_manager.assign_parcel_to_courier'))

    # Get all parcels with status "Registered"
    parcels = db.session.query(Parcel).join(ParcelStatus).filter(ParcelStatus.Status_Type == 'Registered').all()
    
    # Fetch all couriers
    couriers = Courier.query.all()

    # Prepare the data to be passed to the template
    parcel_data = []
    for parcel in parcels:
        sender_name = parcel.sender.User_Name if parcel.sender else 'Unknown'
        recipient_name = parcel.recipient.User_Name if parcel.recipient else 'Unknown'
        destination = parcel.recipient.get_university_name() if parcel.recipient else 'Unknown'
        status = 'Registered'  # Since we filtered by "Registered" status

        parcel_data.append({
            'Parcel_ID': parcel.Parcel_ID,
            'Sender_Name': sender_name,
            'Recipient_Name': recipient_name,
            'Destination': destination,
            'Status': status
        })

    return render_template('ParcelManager/AssignParcelToCourier.html', parcels=parcel_data, couriers=couriers)

