from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import User, db
from flask_login import login_user

# Create authentication blueprint for handling relevant routes (signup, login, logout, etc.)
auth = Blueprint('auth', __name__)

@auth.route('/login.html')
def redirectLogin():
    return redirect('/login', code=302)

@auth.route('/login')
def login():
    logged_in = False  # Temporary logged-in value for now, changes header appearance
    return render_template('login.html', logged_in=logged_in)

@auth.route('/login', methods=['POST'])
def login_post():
    # Retrieve inputted login details
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False  # Remember login info for the user if they choose this

    user = User.query.filter_by(email=email).first()

    # If the user does not exist or the password is wrong, redirect back to the login page
    if not user or not user.check_password(password):
        flash('Incorrect email or password.')
        if user:
            if user.failed_signin_attempts > 5:
                flash('This account is locked. Please contact support to unlock your account and reset your password.')
            else:
                user.failed_signin_attempts += 1
                db.session.commit()
        return redirect(url_for('auth.login'))

    # Redirect to the profile page if login is successful, reset failed sign-in attempts
    if user.failed_signin_attempts <= 5:
        login_user(user, remember=remember)
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

        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        name = request.form.get("name")

        user_email = User.query.filter_by(email=email).first()
        if user_email:
            flash("This email already exists.")
            return redirect(url_for("auth.register"))
        user_name = User.query.filter_by(username=username).first()
        if user_name:
            flash("This username already exists.")
            return redirect(url_for("auth.register"))
        if len(username) == 0:
            flash("You must provide a username.")
            return redirect(url_for("auth.register"))
        if len(password) == 0:
            flash("You must provide a password.")
            return redirect(url_for("auth.register"))
        if confirm_password != password:
            flash("The passwords do not match!")
            return redirect(url_for("auth.register"))
        if len(name) == 0:
            flash("You must provide your name.")
            return redirect(url_for("auth.register"))

        new_user = User(email=email, username=username, password=password, name=name)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Successful!")

        return redirect(url_for("main.profile"))  # Redirect to the profile page

    else:
        return render_template("register.html")
