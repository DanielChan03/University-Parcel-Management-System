from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
from flask_login import current_user, login_required
from webapp.models import Parcel, ParcelStatus, db
from webapp.Couriercode.notifications import add_notification
import random

report_parcel_bp = Blueprint('report_parcel_issue', __name__)

@report_parcel_bp.route('/report-parcel', methods=['GET', 'POST'])
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

        # Send notifications to all involved parties
        sender_email = parcel.sender.User_Email  # Sender's email
        recipient_email = parcel.recipient.User_Email  # Recipient's email
        send_manager_email = parcel.send_manager.Manager_Email if parcel.send_manager else None  # Send manager's email
        receive_manager_email = parcel.receive_manager.Manager_Email if parcel.receive_manager else None  # Receive manager's email

        # Notification title and message
        notification_title = f"{status_type} for Parcel {parcel_id}."
        notification_message = f"This is an auto-generated notification, do not reply!\n\nIssue Description: {issue_description}"

        # Send notifications
        add_notification(sender_email, notification_title, notification_message, current_user.Courier_Email)
        add_notification(recipient_email, notification_title, notification_message, current_user.Courier_Email)
        if send_manager_email:
            add_notification(send_manager_email, notification_title, notification_message, current_user.Courier_Email)
        if receive_manager_email:
            add_notification(receive_manager_email, notification_title, notification_message, current_user.Courier_Email)

        flash("Parcel issue reported successfully!", "success")
        return redirect(url_for('report_parcel_issue.report_parcel'))  # Redirect to avoid resubmission

    return render_template("Courier/CourierReportDelivery.html")
