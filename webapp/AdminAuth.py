from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from .models import Admin
from . import db

admin_auth = Blueprint('admin_auth', __name__)

# Admin Login
@admin_auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user is an Admin
        admin = Admin.query.filter_by(Admin_Email=email).first()
        if admin:
            if check_password_hash(admin.Admin_Password, password):
                flash('Logged in successfully as Admin!', category='success')
                login_user(admin, remember=True)
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("Admin/AdminLogin.html")

# Admin Logout
@admin_auth.route('/admin-logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out successfully.', category='success')
    return redirect(url_for('admin_auth.admin_login'))