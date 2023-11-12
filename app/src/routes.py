from flask import Blueprint, jsonify
from flask_login import login_required, current_user

routes = Blueprint('routes', __name__)

@routes.route('/user_stats', methods=['GET'])
@login_required
def get_user_stats():
    
    user = current_user
    
    return jsonify({
        'streak': user.streak,
        'points': user.points
    })
