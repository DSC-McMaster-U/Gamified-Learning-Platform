from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User, db, GradeEnum, UserProgress, Points, Teacher
from flask_login import login_user
from .utils.passwordStrength import check_password_strength
from .utils.calculateAge import calculate_age

# Create authentication blueprint for handling relevant routes (signup, login, logout, etc.)
auth = Blueprint('auth', __name__)

@auth.route('/login.html')
def redirectLogin():
    return redirect('/login', code=302)

@auth.route('/login')
def login(): 
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

    # Determine if the email belongs to a Teacher or a User
    account = teacher if teacher else user

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
            return redirect(url_for('main.profile'))
        else:  # account is an instance of Teacher
            return render_template('temp_teacher_redirect.html')
    else:
        flash('This account is locked. Please contact support to unlock your account and reset your password.', 'login_error')
        return redirect(url_for('auth.login'))

@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        name = request.form.get("name")
        username = request.form.get("username")
        date_of_birth = request.form.get("date_of_birth")
        email = request.form.get("email")
        confirm_email = request.form.get("confirm_email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role") # get the position of the role switch at time of submission

        age = calculate_age(date_of_birth)
        if role == "teacher":
            user_email = Teacher.query.filter_by(email=email).first()
            user_name = Teacher.query.filter_by(username=username).first()
        else:
            user_email = User.query.filter_by(email=email).first()
            user_name = User.query.filter_by(username=username).first()

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
        return render_template("register.html", logged_in=False)
