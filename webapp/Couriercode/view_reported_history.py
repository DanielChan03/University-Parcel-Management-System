from flask import Blueprint, render_template
from flask_login import current_user, login_required
from webapp.models import Delivery, Parcel, ParcelStatus, StudentStaff, University

view_reported_history_bp = Blueprint('view_reported_history', __name__)

@view_reported_history_bp.route('/view_reported_history')
@login_required
def viewReportedHistory():
    # Get the current courier's ID
    current_courier_id = current_user.Courier_ID

    # Query the Delivery table to find deliveries associated with the current courier
    courier_deliveries = Delivery.query.filter_by(Courier_ID=current_courier_id).all()

    # Prepare a list to store the reported history data
    reported_history = []

    # Loop through each delivery associated with the current courier
    for delivery in courier_deliveries:
        # Query the Parcel table to find parcels associated with the current delivery
        parcels = Parcel.query.filter_by(Delivery_ID=delivery.Delivery_ID).all()

        # Loop through each parcel
        for parcel in parcels:
            # Query the ParcelStatus table to find statuses starting with "Reported - %" for the current parcel
            reported_statuses = ParcelStatus.query.filter(
                ParcelStatus.Parcel_ID == parcel.Parcel_ID,
                ParcelStatus.Status_Type.like('Reported - %')
            ).all()

            # Loop through each reported status
            for status in reported_statuses:
                # Fetch the recipient's details
                recipient = StudentStaff.query.get(parcel.Recipient_User_ID)
                if recipient:
                    # Fetch the recipient's university (destination)
                    university = University.query.get(recipient.University_ID)
                    if university:
                        # Add the reported history data to the list
                        reported_history.append({
                            "Parcel_ID": parcel.Parcel_ID,
                            "Reported_Title": status.Status_Type,  # The reported status (e.g., "Reported - Damaged")
                            "Parcel_Destination": university.University_Name+ ", " + university.University_Location,  # Destination (university location)
                            "Reported_At": status.Updated_At  # Timestamp when the status was updated
                        })

    # Render the template with the reported history data
    return render_template('Courier/CourierReportedHistory.html', reported_history=reported_history)
