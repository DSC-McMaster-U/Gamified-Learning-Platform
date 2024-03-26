from flask import Blueprint, session, render_template, url_for, redirect, request, current_app
from flask_login import login_required, current_user, logout_user
from functools import reduce
from .models import *
from sqlalchemy import or_

main = Blueprint('main', __name__)

# Call this function to get a dict of common user data that should always be sent to the front-end
def returnLoggedInData() -> dict:
    # Assuming that registration is implemented correctly and user should only be one of two roles, we check for
    # which role table they exist within
    studentCheck = User.query.filter_by(email=current_user.email).first()
    teacherCheck = Teacher.query.filter_by(email=current_user.email).first()
    
    output = {
        "name": current_user.name, 
        "age": current_user.age,
        "username": current_user.username,
        "email": current_user.email,
        "grade": None if teacherCheck and not studentCheck else current_user.grade.value,
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

    modules = Module.query.filter_by(course_id=course_id).all()

    topics = {}
    for module in modules:
        topics[module.id] = Topic.query.filter_by(module_id=module.id).all()

    # Send in number of topics for a course to display on lessons page, easier to compute here than accessing dict values with Jinja2
    number_topics = sum(len(module_topics) for module_topics in topics.values())

    lessons = {}
    for module_topics in topics.values():
        for topic in module_topics:
            lessons[topic.id] = Lesson.query.filter_by(topic_id=topic.id).all()

    return render_template('lesson.html', show_footer=True, course=course, modules=modules, topics=topics, number_topics=number_topics, lessons=lessons, **loggedInUser)

@main.route('/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def quiz_page(quiz_id):
    loggedInUser = returnLoggedInData()

    quiz : Quiz = Quiz.query.get(quiz_id)

    # Workaround if there are no quizzes or related questions right now, just to prevent an error
    if not quiz or not questions:
        # Delete any temp sample tests similar to the one that will be created below
        deleteQuizzes = Quiz.query.filter(or_(Quiz.title=="Prime Factorization", Quiz.title=="Test Activity Debug 2")).all()

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
            title="Prime Factorization",
            subject_type=Subject.COMPSCI,
            # id=sampleActivity.id,
            active=False,
            level=1,
            score=0
        )

        db.session.add(sampleQuiz)
        db.session.commit()
        quiz: Quiz = Quiz.query.filter_by(title="Prime Factorization").first()

        sampleQ1 = QuizQuestion(
            quiz_id=quiz.id,
            question_content="Which of the following is not a prime number?"
        )

        sampleQ2 = QuizQuestion(
            quiz_id=quiz.id,
            question_content="What is the prime factorization of 150?"
        )

        sampleQ3 = QuizQuestion(
            quiz_id=quiz.id,
            question_content="Making a factor tree is not an effective way to demonstrate the prime factorization of a number."
        )

        db.session.add_all([sampleQ1, sampleQ2, sampleQ3])
        db.session.commit()
        questions = {
            qNum: question for qNum, question in enumerate(QuizQuestion.query.filter_by(quiz_id = quiz.id).order_by().all())
        }
        # print(questions)
        sampleQ1Ans = [
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[0].id,
                correct = False,
                answer_content="2"
            ),
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[0].id,
                correct = False,
                answer_content="3"
            ),
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[0].id,
                correct = True,
                answer_content="4"
            ),
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[0].id,
                correct = False,
                answer_content="5"
            ),
        ]

        sampleQ2Ans = [
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[1].id,
                correct = True,
                answer_content="2 × 3 × 5²"
            ),
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[1].id,
                correct = False,
                answer_content="2² × 3² × 5²"
            ),
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[1].id,
                correct = False,
                answer_content="3² + 4² + 5³"
            ),
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[1].id,
                correct = False,
                answer_content="2³ × 3 × 5²"
            ),
        ]

        sampleQ3Ans = [
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[2].id,
                correct = True,
                answer_content="True"
            ),
            QuizAnswer(
                quiz_id=quiz.id,
                quiz_question_id=questions[2].id,
                correct = False,
                answer_content="False"
            )
        ]

        db.session.add_all(sampleQ1Ans)
        db.session.add_all(sampleQ2Ans)
        db.session.add_all(sampleQ3Ans)
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

@main.route('/quiz-result', methods=['GET'])
@login_required
def quiz_results():
    loggedInUser = returnLoggedInData()
    user_score = session["quiz_score"]
    totalNumQs = session["quiz_num_q"]

    return render_template(
        "quizResults.html", 
        score=user_score, 
        num_questions=totalNumQs, 
        **loggedInUser
    )

@main.route('/dashboard')
@login_required
def dashboard_page():
    loggedInUser = returnLoggedInData()

    if loggedInUser["role"] == "Teacher":
        return redirect(url_for("main.teacher_page"))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PER_PAGE']

    user_progress = current_user.progress 
    user_points = current_user.points 
    leaderboard_data = Points.get_leaderboard()
    leaderboard_page = User.query.join(Points).order_by(Points.points.desc()).paginate(page=page, per_page=per_page,
                            error_out=False)

    return render_template(
        'dashboard.html', 
        user_progress=user_progress, 
        # leaderboard_data=leaderboard_data,
        leaderboard_data=leaderboard_page.items,
        enumerate=enumerate,     # pass Python's enumerate() function to be used within Jinja2
        **loggedInUser
    )

@main.route('/test/dashboard')
def test_dashboard():
    loggedInUser = returnLoggedInData()

    return render_template('dashboard.html', **loggedInUser)

@main.route('/leaderboard')
@login_required
def leaderboard_page():
    loggedInUser = returnLoggedInData()

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PER_PAGE']
    leaderboard_page = User.query.join(Points).order_by(Points.points.desc()).paginate(page=page, per_page=per_page,
                            error_out=False)
    leaderboard_data=leaderboard_page.items

    user_ranking = None
    user_points = Points.query.filter_by(user_id=current_user.id).first()

    if user_points:
        user_ranking = Points.query.filter(Points.points >= user_points.points).filter(Points.user_id < current_user.id).count() + 1
        print(current_user.id)
    # Add dummy spots to fill up the leaderboard, if there's less than 6 users and only one page
    if not leaderboard_page.has_next and page == 1 and len(leaderboard_data) < 7:
        prev_length = len(leaderboard_data)

        for i in range(7 - prev_length):
            leaderboard_data.append({
                "name": "---", 
                "points": {
                    "points": "---"
                }
            })

    return render_template(
        'leaderboard.html', 
        leaderboard_data=leaderboard_data, 
        user_ranking=user_ranking,
        current_page=page,
        has_next=leaderboard_page.has_next,
        next_page=page + 1 if leaderboard_page.has_next else None,
        **loggedInUser
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
    loggedInUser = returnLoggedInData()

    if loggedInUser["role"] == "Student":
        return redirect(url_for("main.dashboard_page"))
    
    return render_template(
        'teachers.html', 
        **loggedInUser
    )
    
@main.route('/contact')
def contact_page():
    return render_template('contact.html')


@main.route('/logout')
@login_required
def log_out():
    logout_user()
    print(current_user)
    session["login_type"] = None

    return redirect(url_for('auth.login'))