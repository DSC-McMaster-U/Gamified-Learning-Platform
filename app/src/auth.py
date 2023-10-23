from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import User
from . import db

# create authentication blueprint for handling relevant routes (signup, login, logout, etc.)
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # retrieve inputted login details 
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False # remember login info for user if they choose this

    user = User.query.filter_by(email=email).first() # if email is inputted, check for the email in database

    # if the user does not exist or password is wrong, redirect back to login page
    if not user or not user.check_password(password):
        flash('Incorrect email or password.')
        # increment failed signin attempts or display locked account
        if user:
            if user.failed_signin_attempts > 5:
                flash('This account is locked. Please contact support to unlock your account and reset your password.')
            else:
                user.failed_signin_attempts += 1
                db.session.commit()
        return redirect(url_for('auth.login'))
    
    # redirect to profile page if login is successful, reset failed sign-in attempts
    if user.failed_signin_attempts <= 5:
        user.failed_signin_attempts = 0
        db.session.commit()
        flash('Successfully logged in! Redirecting to dashboard...')
        return redirect(url_for('main.profile'))
    else:
        flash('This account is locked. Please contact support to unlock your account and reset your password.')
        return redirect(url_for('auth.login'))