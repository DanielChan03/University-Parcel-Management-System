from flask import Blueprint, render_template, session, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from .models import  Parcel, ParcelStatus, Waitlist, ParcelManager, Courier, SmartLocker, Delivery, db
from werkzeug.security import generate_password_hash
import random
import string
from datetime import datetime  # Import the datetime class

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

@parcel_manager.route('/organize-parcel', methods=['GET', 'POST'])
def organize_parcel():
    if request.method == 'POST':
        parcel_id = request.form.get('parcel_id')
        courier_id = request.form.get('courier_id')

        if not parcel_id or not courier_id:
            flash("Please select both a parcel and a courier!", "error")
            return redirect(url_for('parcel_manager.organize_parcel'))

        parcel = Parcel.query.get(parcel_id)
        courier = Courier.query.get(courier_id)

        if parcel and courier:
            # Check if the parcel already has a delivery assigned
            if parcel.Delivery_ID:
                # Update the existing delivery record with the new courier_id
                delivery = Delivery.query.get(parcel.Delivery_ID)
                if delivery:
                    delivery.Courier_ID = courier.Courier_ID
                    db.session.commit()
                    flash(f"Parcel {parcel_id} reassigned to Courier {courier.Courier_ID} successfully!", "success")
                else:
                    flash(f"Delivery record not found for Parcel {parcel_id}!", "error")
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
            # Function to generate a unique Status_ID
            def generate_unique_status_id():
                while True:
                    status_id = f"{''.join(random.choices(string.ascii_uppercase, k=3))}{''.join(random.choices('0123456789', k=8))}"
                    if not ParcelStatus.query.filter_by(Status_ID=status_id).first():
                        return status_id

            # Assign a unique Status_ID
            status_id = generate_unique_status_id()
            # Update the parcel status to "Assigned to Courier"
            new_status = ParcelStatus(
                Status_ID=status_id,
                Parcel_ID=parcel.Parcel_ID,
                Status_Type="Assigned to Courier",  # Or "Out for Delivery"
                Updated_by=current_user.Manager_ID,
                Updated_At=datetime.utcnow()
            )
            db.session.add(new_status)
            db.session.commit()

            # Add a notification for the courier
            if 'courier_notifications' not in session:
                session['courier_notifications'] = {}

            courier_notifications = session['courier_notifications']
            if courier_id not in courier_notifications:
                courier_notifications[courier_id] = []

            courier_notifications[courier_id].append({
                'parcel_id': parcel_id,
                'message': f"Parcel {parcel_id} has been assigned to you.",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            session['courier_notifications'] = courier_notifications
            session.modified = True

        else:
            flash("Invalid parcel or courier selected!", "error")

        return redirect(url_for('parcel_manager.organize_parcel'))

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

    return render_template('ParcelManager/OrganizeParcel.html', parcels=parcel_data, couriers=couriers)

@parcel_manager.route('/update_parcel_status', methods=['GET', 'POST'])
def update_parcel_status():
    # Fetch all parcels from database
    parcels = Parcel.query.all()
    statuses = ParcelStatus.query.all()


    if request.method == 'POST':
        parcelID = request.form['Parcel_ID']
        updateStatus = request.form.get('Update_Status')

        try:
            # Find the existing parcel status record
            parcel_status = ParcelStatus.query.filter_by(Parcel_ID=parcelID).first()

            if parcel_status:
                # Update the status type and timestamp
                parcel_status.Status_Type = updateStatus
                parcel_status.Updated_by = current_user.Manager_ID  # Make sure this attribute exists
                parcel_status.Updated_At = datetime.utcnow()
            db.session.commit()

            flash('Parcel status updated successfully!', category='success')

            return redirect(url_for('parcel_manager.update_parcel_status'))


        except NoResultFound:
            pass

    return render_template(
        'ParcelManager/ParcelManagerUpdateParcelStatus.html', 
        parcels = parcels, 
        statuses = statuses,
        )

@parcel_manager.route('/monitor_locker_issue', methods=['GET', 'POST'])
def monitor_locker_issue():
    # Get search query
    lockerFilter = request.args.get('filter')

    if lockerFilter:
        lockers = SmartLocker.query.filter(SmartLocker.Locker_ID.ilike(f'%{lockerFilter}%')).all()
    else:
        lockers = SmartLocker.query.all()
    
    return render_template(
        "ParcelManager/ParcelManagerMonitorLockerIssue.html",
        lockers = lockers
    )


@parcel_manager.route('/log_arrival_parcel', methods=['GET', 'POST'])
def log_arrival_parcel():
    parcels = Parcel.query.all()
    statuses = ["Verified", "Missing"]

    if request.method == 'POST':
        parcelID = request.form.get('Parcel_ID')      
        updateStatus = request.form.get('Update_Status')

        try:
            # Find the existing parcel status record
            parcel_status = ParcelStatus.query.filter_by(Parcel_ID=parcelID).first()

            if parcel_status:
                # Update the status type and timestamp
                parcel_status.Status_Type = updateStatus
                parcel_status.Updated_by = current_user.Manager_ID  # Make sure this attribute exists
                parcel_status.Updated_At = datetime.utcnow()
                db.session.commit()
    
                flash('Parcel status updated successfully!', category='success')
                
            else:
                flash('Parcel status not found!', category='error')
                
            return redirect(url_for('parcel_manager.log_arrival_parcel'))


        except NoResultFound:
            pass

    return render_template(
        'ParcelManager/ParcelManagerLogArrivalParcel.html',
        parcels = parcels,
        statuses = statuses,
        )

