from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash
from models import db, User
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods=["GET", "POST"])
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
        new_user = User(email=email, username=username, password=generate_password_hash(password), first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Successful!")

        return redirect(url_for("user_profile.html"))

    #Display register screen
    else:
        return render_template("register.html")


