from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import reduce
from .models import *

main = Blueprint('main', __name__)

# Call this function to get a dict of common user data that should always be sent to the front-end
def returnLoggedInData() -> dict:
    # Assuming that registration is implemented correctly and user should only be one of two roles, we check for
    # which role table they exist within
    studentCheck = User.query.filter_by(email=current_user.email).first()
    teacherCheck = Teacher.query.filter_by(email=current_user.email).first()
    
    output = {
        "name": current_user.name, 
        "username": current_user.username,
        "email": current_user.email,
        "age": current_user.age,
        "grade": current_user.grade.value,
        "current_user": current_user, 
        "role": "Teacher" if teacherCheck and not studentCheck else "Student",
        "logged_in": True
    }

    return output

@main.route('/profile')
@login_required
def profile():
    # Receives a dict of user info variables, which will be unpacked as separate args to Jinja
    loggedInUser: dict = returnLoggedInData()

    return render_template(
        'user_profile.html', 
        show_footer=True,
        **loggedInUser    # Unpack all dict key-value pairs here
    )
    
@main.route('/lesson/<int:course_id>')
@login_required
def lesson_page(course_id):
    loggedInUser: dict = returnLoggedInData()
    course = Course.query.get(course_id)

    # TODO: set up a conditional (like below in quiz_page) and an algorithm that parses 
    #       through course structure + lesson content and sends two dictionaries in a particular 
    #       format over to front-end, where it can be processed to generate an appropriate tab 
    #       structure and panel contents.
    return render_template('lesson.html', show_footer=True, **loggedInUser)

@main.route('/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def quiz_page(quiz_id):
    loggedInUser = returnLoggedInData()

    quiz : Quiz = Quiz.query.get(quiz_id)

    # Workaround if there are no quizzes or related questions right now, just to prevent an error
    if not quiz or not questions:
        # Delete any temp sample tests similar to the one that will be created below
        deleteQuizzes = Quiz.query.filter_by(title="Test Activity Debug 2").all()

        for deleteQuiz in deleteQuizzes:
            deleteQuizQs = QuizQuestion.query.filter_by(quiz_id = deleteQuiz.id).all()
            deleteQuizAns2D = [
                QuizAnswer.query.filter_by(quiz_id = deleteQuiz.id, quiz_question_id = deleteQuizQ.id).all() for deleteQuizQ in deleteQuizQs
            ]
            deleteQuizAns = list(reduce(lambda x, y : x + y, deleteQuizAns2D, []))   # Flatten the 2D answers list above into 1D

            for deleteEntity in (deleteQuizQs + deleteQuizAns):
                db.session.delete(deleteEntity)
            
            db.session.delete(deleteQuiz)

        db.session.commit()
        # print(Quiz.query.filter_by(title="Test Activity Debug 2").all())  <-- should be empty

        # Temporary for now...? Add a sample quiz w/ 2 Q's, 4 answers each as a placeholder in case of errors/invalid quiz ID query
        sampleQuiz = Quiz(
            title="Test Activity Debug 2",
            subject_type=Subject.COMPSCI,
            # id=sampleActivity.id,
            active=False,
            level=1,
            score=0
        )

        db.session.add(sampleQuiz)
        db.session.commit()
        quiz: Quiz = Quiz.query.filter_by(title="Test Activity Debug 2").first()

        sampleQ1 = QuizQuestion(
            quiz_id=quiz.id,
            question_content="This is a sample question for you to answer. What is the answer?"
        )

        sampleQ2 = QuizQuestion(
            quiz_id=quiz.id,
            question_content="Test question #2:"
        )

        db.session.add_all([sampleQ1, sampleQ2])
        db.session.commit()
        questions = {
            qNum: question for qNum, question in enumerate(QuizQuestion.query.filter_by(quiz_id = quiz.id).order_by().all())
        }
        # print(questions)

        sampleQ1Ans = [
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[0].id,
                correct = True if ansNum == 4 else False,
                answer_content=f"Answer #1-{ansNum}"
            ) for ansNum in range(1, 5)
        ]

        sampleQ2Ans = [
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[1].id,
                correct = True if ansNum == 2 else False,
                answer_content=f"Answer #2-{ansNum}"
            ) for ansNum in range(1, 5)
        ]

        db.session.add_all(sampleQ1Ans)
        db.session.add_all(sampleQ2Ans)
        db.session.commit()

        answers = {
            quizQ[0]: QuizAnswer.query.filter_by(quiz_id = quiz.id, quiz_question_id = quizQ[1].id).all() for quizQ in list(questions.items())
        }
    else:
        questions = {
            qNum: question for qNum, question in enumerate(QuizQuestion.query.filter_by(quiz_id = quiz.id).order_by().all())
        }
        answers = {
            quizQ[0]: QuizAnswer.query.filter_by(quiz_id = quiz.id, quiz_question_id = quizQ[1].id).all() for quizQ in list(questions.items())
        }

    # print(questions)
    # print(answers)
    return render_template('quiz.html', show_footer=True, quiz=quiz, questions=questions, answers=answers, **loggedInUser)

@main.route('/dashboard')
@login_required
def dashboard_page():
    loggedInUser = returnLoggedInData()

    user_progress = current_user.progress
    user_points = current_user.points
    return render_template('dashboard.html', show_footer=True, user_progress=user_progress, **loggedInUser)

@main.route('/test/dashboard')
def test_dashboard():
    loggedInUser = returnLoggedInData()

    return render_template('dashboard.html', **loggedInUser)

@main.route('/leaderboard')
@login_required
def leaderboard_page():
    loggedInUser = returnLoggedInData()


    leaderboard_data = Points.get_leaderboard()
    user_ranking = None
    
    user_points = Points.query.filter_by(user_id=current_user.id).first()
    if user_points:
        user_ranking = Points.query.filter(Points.points > user_points.points).count() + 1

    
    
    
    return render_template(
        'leaderboard.html', 
        leaderboard_data=leaderboard_data, 
        user_ranking=user_ranking,
        **loggedInUser
    )