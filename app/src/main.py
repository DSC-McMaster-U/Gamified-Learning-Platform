from flask import Blueprint, render_template, request, current_app
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
    leaderboard_data = Points.get_leaderboard()

    return render_template(
        'dashboard.html', 
        current_user=current_user, 
        logged_in=True, 
        user_progress=user_progress, 
        leaderboard_data=leaderboard_data)

@main.route('/test/dashboard')
def test_dashboard():
    return render_template('dashboard.html')

@main.route('/leaderboard')
@login_required
def leaderboard_page():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PER_PAGE']

    leaderboard_page = User.query.join(Points).order_by(Points.points.desc()).paginate(page=page, per_page=per_page,
                            error_out=False)

    user_ranking = None
    
    user_points = Points.query.filter_by(user_id=current_user.id).first()
    if user_points:
        user_ranking = Points.query.filter(Points.points > user_points.points).count() + 1
    
    return render_template(
        'leaderboard.html', 
        name=current_user.name, 
        username=current_user.username,
        leaderboard_data=leaderboard_page.items, 
        user_ranking=user_ranking,
        logged_in=True,
        current_page=page,
        has_next=leaderboard_page.has_next,
        next_page=page + 1 if leaderboard_page.has_next else None
    )

@main.route('/teacher')
@login_required
def teacher_page():
    '''
    teachers = Teacher.query.filter_by(tid=current_user.username).first()


    if not teachers:
        teachers = None;

    courses_instructing = teachers.courses
    students_instructing = teachers.students
    modules = teachers.modules
    topics = teachers.topics

    return render_template(
        'teachers.html', 
        current_user=current_user, 
        courses_instructing=courses_instructing, 
        students_instructing=students_instructing,  
        module=modules, 
        topic=topics, 
        logged_in=True)
        '''
    return render_template(
        'teachers.html', 
        name=current_user.name, 
        username=current_user.username,
        email=current_user.email,
        age=current_user.age,
        grade=current_user.grade.value,
        current_user=current_user, 
        logged_in=True)