from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import *

main = Blueprint('main', __name__)

@main.route('/profile')
@login_required
def profile():
    return render_template(
        'user_profile.html', 
        name=current_user.name, 
        username=current_user.username,
        email=current_user.email,
        age=current_user.age,
        grade=current_user.grade.value,
        current_user=current_user, 
        logged_in=True
    )
    
@main.route('/lesson/<int:course_id>')
@login_required
def lesson_page(course_id):
    course = Course.query.get(course_id)

    # TODO: set up a conditional (like below in quiz_page) and an algorithm that parses 
    #       through course structure + lesson content and sends two dictionaries in a particular 
    #       format over to front-end, where it can be processed to generate an appropriate tab 
    #       structure and panel contents.
    return render_template('lesson.html', current_user=current_user, logged_in=True)

@main.route('/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def quiz_page(quiz_id):
    quiz = Quiz.query.get(quiz_id)

    # Temporary workaround since there are no quizzes right now, just to prevent an error
    if not quiz:
        questions = None
    else:
        questions = [(i + 1, question) for i, question in enumerate(quiz.questions)]

    return render_template('quiz.html', current_user=current_user, logged_in=True, quiz=quiz, questions=questions)

@main.route('/dashboard')
@login_required
def dashboard_page():
    user_progress = current_user.progress
    user_points = current_user.points
    return render_template('dashboard.html', current_user=current_user, logged_in=True, user_progress=user_progress)

@main.route('/test/dashboard')
def test_dashboard():
    return render_template('dashboard.html')