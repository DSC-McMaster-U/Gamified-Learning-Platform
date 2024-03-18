from flask import Blueprint, render_template, redirect, session, url_for, request, flash
from .models import User, db, GradeEnum, UserProgress, Points, Teacher
from flask_login import login_user, current_user
from .utils.passwordStrength import check_password_strength
from .utils.calculateAge import calculate_age
import re

# Create authentication blueprint for handling relevant routes (signup, login, logout, etc.)
auth = Blueprint('auth', __name__)

@auth.route('/login.html')
def redirectLogin():
    return redirect('/login', code=302)

@auth.route('/login')
def login(): 
    if session.get('login_type') is None:
        session['login_type'] = None

    if current_user.is_authenticated:  # already logged in
        studentCheck = User.query.filter_by(email=current_user.email).first()
        teacherCheck = Teacher.query.filter_by(email=current_user.email).first()
        
        if teacherCheck and not studentCheck:
            return redirect(url_for('main.teacher_page'))
        else:
            return redirect(url_for('main.profile'))
        
    return render_template('login.html', logged_in=False) # Temporary logged-in value for now, changes header appearance

@auth.route('/login', methods=['POST'])
def login_post():
    # Retrieve inputted login details
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False  # Remember login info for the user if they choose this

    # Check both User and Teacher tables
    user = User.query.filter_by(email=email).first()
    teacher = Teacher.query.filter_by(email=email).first()

    account = None

    # Determine if the email belongs to a Teacher or a User
    if teacher and not user:
        account = teacher
    elif user and not teacher:
        account = user
    elif user and teacher:
        flash('The email address is associated with multiple roles. Please contact support.', 'login_error')
        return redirect(url_for('auth.login'))
        

    # If no account is found or the password is incorrect, redirect back to the login page
    if not account or not account.check_password(password):
        if account:
            if account.failed_signin_attempts > 5:
                flash('This account is locked. Please contact support to unlock your account and reset your password.', 'login_error')
            else:
                flash('Incorrect password. Try again or click Forgot password to reset it.', 'login_error')
                account.failed_signin_attempts += 1
                db.session.commit()

        else:
            flash('A user with this email does not exist!', 'login_error')

        return redirect(url_for('auth.login'))

    # Redirect to the profile page if login is successful, reset failed sign-in attempts
    if account.failed_signin_attempts <= 5:
        login_user(account, remember=remember)
        account.failed_signin_attempts = 0
        db.session.commit()
        flash('Successfully logged in! Redirecting to dashboard...', 'login_success')
        if isinstance(account, User):
            session['login_type'] = "student"
            return redirect(url_for('main.profile'))
        else:  # account is an instance of Teacher
            session['login_type'] = "teacher"
            return redirect(url_for('main.teacher_page'))
    else:
        flash('This account is locked. Please contact support to unlock your account and reset your password.', 'login_error')
        return redirect(url_for('auth.login'))

@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if session.get('login_type') is None:
        session['login_type'] = None

    if request.method == "POST":

        role = request.form.get("role") # get the position of the role switch at time of submission
        name = request.form.get("name")
        username = request.form.get("username")
        date_of_birth = request.form.get("date_of_birth")
        email = request.form.get("email")
        confirm_email = request.form.get("confirm_email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        yrs_experience = 0

        age = calculate_age(date_of_birth)

        user_email = User.query.filter_by(email=email).first() or Teacher.query.filter_by(email=email).first()
        user_name = User.query.filter_by(username=username).first() or Teacher.query.filter_by(username=username).first()

        if len(name) == 0:
            flash("You must provide your name.", "register_error")
            return redirect(url_for("auth.register"))
        if user_name:
            flash("This username already exists.", "register_error")
            return redirect(url_for("auth.register"))
        if len(username) == 0:
            flash("You must provide a username.", "register_error")
            return redirect(url_for("auth.register"))
        if user_email:
            flash("This email already exists.", "register_error")
            return redirect(url_for("auth.register"))   
        if not re.search("^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$", email):
            flash("You must provide a valid email address.", "register_error")
            return redirect(url_for("auth.register"))
        if confirm_email != email:
            flash("The emails do not match!", "register_error")
            return redirect(url_for("auth.register"))             
        if len(password) == 0:
            flash("You must provide a password.", "register_error")
            return redirect(url_for("auth.register"))
        if confirm_password != password:
            flash("The passwords do not match!", "register_error")
            return redirect(url_for("auth.register"))
        

        # checking password strength
        result = check_password_strength(password)
        if result:
            flash("Password is not strong enough. Here are some suggestions: " + ", ".join(result), "register_error")
            return redirect(url_for("auth.register"))

        if role == "teacher":
            # Create a Teacher object
            new_user = Teacher(
                email=email,
                username=username,
                name=name,
                age=age,
                yrs_experience=yrs_experience
                # Add any other necessary fields specific to Teacher
            )
        else:
            grade = getattr(GradeEnum, request.form.get("grade"))   # Only if student, parses string into GradeEnum field and assigns proper grade
            # Create a User object
            new_user = User(
                email=email,
                username=username,
                name=name,
                grade=grade,
                age=age
            )

        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Assign default lesson id as well??
        if role == "student":
            new_user_progress = UserProgress(
                user_id=new_user.id,
                xp=0,
                level=1,
                next_level_xp=1000,
                current_streak=0,
                longest_streak=0
            )
            db.session.add(new_user_progress)
            db.session.commit()
        
            new_user_points = Points(user_id=new_user.id)

            db.session.add(new_user_progress)
            db.session.commit()

        flash("Registration Successful!")
        return redirect(url_for("auth.login"))

    else:
        if current_user.is_authenticated:  # already logged in
            studentCheck = User.query.filter_by(email=current_user.email).first()
            teacherCheck = Teacher.query.filter_by(email=current_user.email).first()
            
            if teacherCheck and not studentCheck:
                return redirect(url_for('main.teacher_page'))
            else:
                return redirect(url_for('main.profile'))

        return render_template("register.html", logged_in=False)
