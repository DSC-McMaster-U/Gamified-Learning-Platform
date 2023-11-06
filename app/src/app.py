from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import db, User
from .auth import auth as auth_blueprint
from .main import main as main_blueprint
from dotenv import load_dotenv
import os

load_dotenv()

# db = SQLAlchemy()

def create_app(test_config=None):

    app = Flask(__name__)

    # Configure and initalize database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.secret_key = os.getenv('SECRET_KEY')
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    if test_config:
        app.config.update(test_config)
    
    db.init_app(app)

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @login_manager.user_loader
    def load_user(user_id):
        # retrieve the given user from database, user id is the primary key so it will query the correct user
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    return app
