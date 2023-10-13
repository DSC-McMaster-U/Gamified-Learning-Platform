from flask import Blueprint, render_template, redirect, url_for, request
from models import User
from . import db

# create authentication blueprint for handling relevant routes (signup, login, logout, etc.)
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # NOT SURE IF THIS REQUEST WILL WORK TO GET EMAIL OR USERNAME
    input = request.form.get('email_or_username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False # remember login info for user if they choose this

    user = User.query.filter_by(email=input).first() # if email is inputted, check for the email in database

    if not user:
        user = User.query.filter_by(username=input).first() # if username is inputted, check for username

    # if the user does not exist or password is wrong, redirect back to login page
    if not user or not user.check_password(password):
        return redirect(url_for('auth.login'))

    # redirect to profile page if login is successful
    return redirect(url_for('main.profile'))


# @auth.route('/signup')
# def signup():
#     return render_template('signup.html')

# @auth.route('/signup', methods=['POST'])
# def signup_post():
#     email = request.form.get('email')
#     name = request.form.get('name')
#     password = request.form.get('password')
#     username = request.form.get('username')
#     favorite_subject = request.form.get('favorite subject')

#     user = User.query.filter_by(email=email).first() # Perform query to check if user already exists in database

#     if user: # redirect back to signup page if the created user already exists
#         return redirect(url_for('auth.signup'))
    
#     # create a user using the signup information
#     new_user = User(email=email, name=name, username=username, favorite_subject=favorite_subject)
#     new_user.set_password(password)

#     # add the user to the database
#     db.session.add(new_user)
#     db.session.commit()

#     # redirect user to login page after new user has been validated
#     return redirect(url_for('auth.login'))
