from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import db, User, Points
from .auth import auth as auth_blueprint
from .main import main as main_blueprint
from .routes import routes as routes_blueprint
from .lesson_api import api as api_blueprint
from .quizSubmit import quiz as quiz_blueprint
from dotenv import load_dotenv
from sqlalchemy import desc
import os

load_dotenv()

def create_app(test_config=None):

    app = Flask(__name__)

    # Configure and initialize database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.secret_key = os.getenv('SECRET_KEY')
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(routes_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(quiz_blueprint)
    
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
        
    # Pagination configuration
    PER_PAGE = 10

    def sort_leaderboard():
        # Implement your sorting logic here
        # For example, assuming User model has a 'score' field
        return User.query.order_by(User.score.desc()).all()

    @app.route('/leaderboard', methods=['GET'])
    def leaderboard():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', PER_PAGE, type=int)

        leaderboard_data = sort_leaderboard()
        total_users = len(leaderboard_data)

        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_data = leaderboard_data[start_index:end_index]

        # Construct JSON response
        response = {
            'leaderboard_data': [
                {
                    'rank': (page - 1) * per_page + i + 1,
                    'username': user.username,
                    'points': user.points
                } for i, user in enumerate(leaderboard_data)
            ],
            'page': page,
            'per_page': per_page,
            'total_users': total_users
        }

        return jsonify(response)

        # return app
