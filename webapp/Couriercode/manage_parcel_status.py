from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from webapp.models import Delivery, Parcel, ParcelStatus,StudentStaff,University, db
import random

manage_parcel_status_bp = Blueprint('manage_status', __name__)

@manage_parcel_status_bp.route('/manage-parcel-status', methods=['GET', 'POST'])
@login_required
def manage_parcel_status():
    if request.method == 'POST':
        parcel_id = request.form.get('Parcel_ID')
        new_status = request.form.get('Update_Status')

        if not parcel_id or not new_status:
            flash("Parcel ID and status are required.", "danger")
            return redirect(url_for('manage_status.manage_parcel_status'))

        parcel = Parcel.query.filter_by(Parcel_ID=parcel_id).first()
        if not parcel:
            flash("Parcel ID not found.", "danger")
            return redirect(url_for('manage_status.manage_parcel_status'))

        delivery = Delivery.query.filter_by(Delivery_ID=parcel.Delivery_ID, Courier_ID=current_user.Courier_ID).first()
        if not delivery:
            flash("You are not authorized to update this parcel.", "danger")
            return redirect(url_for('manage_status.manage_parcel_status'))

        new_status_id = f"STA{random.randint(100000, 999999)}"
        while db.session.query(ParcelStatus).filter_by(Status_ID=new_status_id).first():
            new_status_id = f"STA{random.randint(100000, 999999)}"

        new_status_entry = ParcelStatus(
            Status_ID=new_status_id,
            Parcel_ID=parcel_id,
            Status_Type=new_status,
            Updated_by=current_user.Courier_ID,
            Updated_At=datetime.now()
        )
        db.session.add(new_status_entry)
        db.session.commit()

        flash("Parcel status updated successfully!", "success")
        return redirect(url_for('manage_status.manage_parcel_status'))

    deliveries = Delivery.query.filter_by(Courier_ID=current_user.Courier_ID).all()
    delivery_ids = [delivery.Delivery_ID for delivery in deliveries]

    parcels = (
        Parcel.query
        .options(
            joinedload(Parcel.sender),
            joinedload(Parcel.recipient),
            joinedload(Parcel.delivery)
        )
        .filter(Parcel.Delivery_ID.in_(delivery_ids))
        .order_by(Parcel.Parcel_ID.asc())
        .all()
    )

    allowed_statuses = [
    "Parcel Collected",
    "Parcel Outgoing",
    "In Transit",
    "Parcel Arrived at University",
    "Parcel Handed Over to Parcel Manager",
    "Verified - Collected",
    "Verified - Missing",
    "Verified - Damaged"
]

    parcel_data = []
    for parcel in parcels:
        # Get all statuses for the parcel in descending order
        status_history = (
            ParcelStatus.query
            .filter_by(Parcel_ID=parcel.Parcel_ID)
            .order_by(ParcelStatus.Updated_At.desc())
            .all()
        )

        current_status = None
        for status in status_history:
            if status.Status_Type in ["Verified - Collected", "Verified - Missing", "Verified - Damaged"]:
                current_status = status.Status_Type
                break  # Stop checking after any "Verified" status
            if not current_status:
                current_status = status.Status_Type  # Take the latest status before "Verified"

        if current_status:
            # Allow "Reported - %" dynamically
            if current_status.startswith("Reported - ") or current_status in allowed_statuses:
                recipient = StudentStaff.query.filter_by(User_ID=parcel.Recipient_User_ID).first()
                destination = University.query.filter_by(University_ID=recipient.University_ID).first().University_Name if recipient else 'Recipient information not found'

                parcel_data.append({
                    'Parcel_ID': parcel.Parcel_ID,
                    'Sender_Name': parcel.sender.User_Name,
                    'Recipient_Name': parcel.recipient.User_Name,
                    'Destination': destination,
                    'Current_Status': current_status,
                    'Allowed_Statuses': [status for status in allowed_statuses if status != current_status]
                })


    return render_template("Courier/CourierManageStatus.html", parcels=parcel_data)
