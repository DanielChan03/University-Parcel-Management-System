from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from .models import ParcelManager
from . import db

parcel_manager_auth = Blueprint('parcel_manager_auth', __name__)

#Parcel Manager Login
@parcel_manager_auth.route('/parcel-manager-login', methods=['GET', 'POST'])
def parcel_manager_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        parcel_manager = ParcelManager.query.filter_by(Manager_Email=email).first()
        if parcel_manager:
            if check_password_hash(parcel_manager.Manager_Password, password):
                flash('Logged in seccessfully as Parcel Manager!', category='success')
                login_user(parcel_manager, remember=True)
                return redirect(url_for('parcel_manager.parcel_manager_dashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("ParcelManager/ParcelManagerLogin.html")

#Parcel Manager Logout
@parcel_manager_auth.route('parcel-manager-logout')
@login_required
def parcel_manager_logout():
    logout_user()
    flash('Logged out successfully.', category='success')
    return redirect(url_for('parcel_manager_auth.parcel_manager_login'))