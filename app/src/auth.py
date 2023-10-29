from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User, db
from flask_login import login_user

# create authentication blueprint for handling relevant routes (signup, login, logout, etc.)
auth = Blueprint('auth', __name__)

# Redirect to ".html"-less url address; might not be necessary
@auth.route('/login.html')
def redirectLogin():
    return redirect('/login', code = 302)   # Probably should change 302 redirect code later

@auth.route('/login')
def login():
    loggedIn = False       # Temp logged-in value for now, changes header appearance
    return render_template('login.html', logged_in = loggedIn)

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
        login_user(user, remember=remember) # log the user in and create the user session
        user.failed_signin_attempts = 0
        db.session.commit()
        flash('Successfully logged in! Redirecting to dashboard...')
        return redirect(url_for('main.profile'))
    else:
        flash('This account is locked. Please contact support to unlock your account and reset your password.')
        return redirect(url_for('auth.login'))
    

@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        #Access the data submitted to form
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")

        #Check if the inputs are valid
        user_email = User.query.filter_by(email=email).first()
        if user_email:
            flash("This email already exists.")
            return redirect(url_for("register"))
        user_name = User.query.filter_by(username=username).first()
        if user_name:
            flash("This username already exists.")
            return redirect(url_for("register"))
        if len(username) == 0:
            flash("You must provide a username.")
            return redirect(url_for("register"))
        if len(password) == 0:
            flash("You must provide a password.")
            return redirect(url_for("register"))
        if confirm_password != password:
            flash("The passwords are not matching!")
            return redirect(url_for("register"))
        if len(first_name) == 0:
            flash("You must provide your first name.")
            return redirect(url_for("register"))
        if len(last_name) == 0:
            flash("You must provide your last name.")
            return redirect(url_for("register"))

        #Add the user to database and login
        new_user = User(email=email, username=username, password=new_user.set_password(password), first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Successful!")

        return redirect(url_for("user_profile.html"))

    #Display register screen
    else:
        return render_template("register.html")