from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User


app = Flask(__name__)

# Configure and initalize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)
db.init_app(app)

# blueprint with authorization routes for the app
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

@login_manager.user_loader
def load_user(user_id):
    # retrieve the given user from database, user id is the primary key so it will query the correct user
    return User.query.get(int(user_id))

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

db.create_all()

