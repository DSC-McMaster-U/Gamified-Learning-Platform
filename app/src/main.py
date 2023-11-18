from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Quiz

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
        logged_in=True
    )
    
@main.route('/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def quiz_page(quiz_id):
    user = current_user
    quiz = Quiz.query.get(quiz_id)

    user_attempted = quiz in user.quizzes

    # Users highest score
    highest_score = 0
    if user_attempted:
        highest_score = quiz.users.filter_by(id=user.id).first().score
    
    # Temporary workaround since there are no quizzes right now, just to prevent an error
    if not quiz:
        questions = None
    else:
        questions = [(i + 1, question) for i, question in enumerate(quiz.questions)]

    return render_template('quiz.html', quiz=quiz, user_attempted=user_attempted, highest_score=highest_score, questions=questions)