from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import StudentStaff, University
from . import db

auth = Blueprint('auth', __name__)

# Student/Staff Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user is a Student/Staff
        user = StudentStaff.query.filter_by(User_Email=email).first()
        if user:
            if check_password_hash(user.User_Password, password):
                flash(f'Logged in successfully as {user.User_Type}!', category='success')
                login_user(user, remember=True)
                user.Login_Status = 'Active'
                db.session.commit()
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("StudentStaffLogin.html", user=current_user)

# Student/Staff Logout
@auth.route('/logout')
@login_required
def logout():
    user = current_user
    if user:
        user.Login_Status = 'Inactive'
        db.session.commit()
    logout_user()
    flash('Logged out successfully.', category='success')
    return redirect(url_for('auth.login'))

# Student/Staff Sign Up
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    universities = University.query.all()
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user_type = request.form.get('userType')
        university_id = request.form.get('university')
        contact = request.form.get('contact')

        user = StudentStaff.query.filter_by(User_Email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif not university_id:
            flash('Please select a university.', category='error')
        elif not contact:
            flash('Contact number is required.', category='error')
        else:
            user_id = StudentStaff.generate_user_id(user_type)
            new_user = StudentStaff(
                User_ID=user_id,
                User_Name=name,
                User_Email=email,
                User_Password=generate_password_hash(password1, method='pbkdf2:sha256'),
                User_Type=user_type,
                University_ID=university_id,
                User_Contact=contact,
                Login_Status='Active'
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("StudentStaffSign_up.html", universities=universities, user=current_user)