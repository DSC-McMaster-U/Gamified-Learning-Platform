from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/profile')
@login_required
def profile():
    return render_template('user_profile.html', name=current_user.name, email=current_user.email)