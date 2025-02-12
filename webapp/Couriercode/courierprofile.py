from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from webapp.models import Courier
courier_profile_bp = Blueprint('courier_profile', __name__)

@courier_profile_bp.route('/courier/profile')
@login_required
def courier_profile():
    if not isinstance(current_user, Courier):
        return redirect(url_for('unauthorized'))

    courier_data = {
        'Courier_ID': current_user.Courier_ID,
        'Courier_Name': current_user.Courier_Name,
        'Courier_Email': current_user.Courier_Email,
        'Courier_Contact': current_user.Courier_Contact,
    }

    return render_template('Courier/CourierProfile.html', courier=courier_data)