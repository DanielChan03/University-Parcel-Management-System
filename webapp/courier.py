from flask import Blueprint, render_template, session, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from .models import Courier, Parcel, ParcelStatus, Delivery, db
from werkzeug.security import generate_password_hash
import random

courier = Blueprint('courier', __name__)

# Courier Dashboard
@courier.route('/courier-dashboard')
@login_required
def courier_dashboard():

    # Fetch active deliveries
    active_delivery = Delivery.query.filter_by(Courier_ID=current_user.Courier_ID).order_by(Delivery.Deliver_Date.desc()).first()

    # Fetch collected parcels count
    collected_parcels = Parcel.query.filter_by(Delivery_ID=active_delivery.Delivery_ID).count() if active_delivery else 0

    # Fetch reported parcels
    reported_parcels = ParcelStatus.query.filter_by(Status_Type='Reported').count()

    # Fetch scheduled deliveries
    scheduled_delivery = Delivery.query.filter_by(Courier_ID=current_user.Courier_ID).order_by(Delivery.Arrival_Date.asc()).first()

    return render_template(
        "Courier/CourierDashboard.html",
        courier=current_user,
        active_delivery_id=active_delivery.Delivery_ID if active_delivery else "None",
        active_delivery_date=active_delivery.Deliver_Date if active_delivery else "N/A",
        collected_parcels=collected_parcels,
        reported_parcels=reported_parcels,
        scheduled_delivery_id=scheduled_delivery.Delivery_ID if scheduled_delivery else "None",
        scheduled_delivery_date=scheduled_delivery.Arrival_Date if scheduled_delivery else "N/A"
    )

# View Assigned Parcels
@courier.route('/assigned-parcels', methods=['GET'])
@login_required
def view_assigned_parcels():
    assigned_parcels = Parcel.query.filter_by(Delivery_ID=current_user.Courier_ID).all()
    return render_template("Courier/CourierAssignedParcels.html", parcels=assigned_parcels)

# Update Parcel Status
@courier.route('/update-parcel-status/<string:parcel_id>', methods=['POST'])
@login_required
def update_parcel_status(parcel_id):
    data = request.get_json()
    new_status = data.get('status')

    parcel_status = ParcelStatus.query.filter_by(Parcel_ID=parcel_id).first()
    if parcel_status:
        parcel_status.Status_Type = new_status
        db.session.commit()
        flash('Parcel status updated successfully!', 'success')
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Parcel not found.'})

# Report an Issue with a Parcel
@courier.route('/report-parcel', methods=['GET'])
@login_required
def report_parcel(parcel_id):
    data = request.get_json()
    issue_description = data.get('issue')

    new_report = ParcelStatus(
        Status_ID=f"REP{random.randint(100000, 999999)}",
        Parcel_ID=parcel_id,
        Status_Type="Reported",
        Updated_by=current_user.Courier_ID
    )
    db.session.add(new_report)
    db.session.commit()

    flash('Parcel issue reported successfully!', 'success')
    return render_template("Courier/CourierReportDelivery.html")


# View Delivery History
@courier.route('/delivery-history', methods=['GET'])
@login_required
def delivery_history():
    deliveries = Delivery.query.filter_by(Courier_ID=current_user.Courier_ID).all()
    return render_template("Courier/CourierDeliveryHistory.html", deliveries=deliveries)




