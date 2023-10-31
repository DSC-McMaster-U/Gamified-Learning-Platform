from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User
from auth import auth as auth_blueprint
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

# Create an instance of Flask-Migrate and associate it with your Flask app and database
migrate = Migrate(app, db)

# Configure and initalize database (need to figure out Google MySQL Cloud)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)
db.init_app(app)

# register blueprint with authorization routes for the app
app.register_blueprint(auth_blueprint)

@login_manager.user_loader
def load_user(user_id):
    # retrieve the given user from database, user id is the primary key so it will query the correct user
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('user_profile.html')

with app.app_context():
    db.create_all()

