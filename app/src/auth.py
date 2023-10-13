from flask import Blueprint, render_template, redirect, url_for, request
from models import User
from . import db

# create authentication blueprint for handling relevant routes (signup, login, logout, etc.)
auth = Blueprint('auth', __name__)

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    username = request.form.get('username')
    favorite_subject = request.form.get('favorite subject')

    user = User.query.filter_by(email=email).first() # Perform query to check if user already exists in database

    if user: # redirect back to signup page if the created user already exists
        return redirect(url_for('auth.signup'))
    
    # create a user using the signup information
    new_user = User(email=email, name=name, username=username, favorite_subject=favorite_subject)
    new_user.set_password(password)

    # add the user to the database
    db.session.add(new_user)
    db.session.commit()

    # redirect user to login page after new user has been validated
    return redirect(url_for('auth.login'))
