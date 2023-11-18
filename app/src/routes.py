from flask import Blueprint, jsonify, request
from .models import * 
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

""" 
Note: To send AJAX requests with forms, create a FormData() variable in JS and append whatever key-value pairs you need
      to it; then include an extra "data" field in the AJAX request and pass the FormData() in it. Also include the extra
      fields "processData" (set to false) and "contentType" (set to either false or "multipart/form-data").
"""

# Create general blueprint for routes
routes = Blueprint("routes", __name__)

# Route to get user stats
@routes.route('/user_stats', methods=['GET'])
@login_required
def get_user_stats():
    
    user = current_user
    
    return jsonify({
        'streak': user.streak,
        'points': user.points
    })

# Route related to a collection of badges
@routes.route("/badges", methods=["GET"])
@login_required
def get_badges():
    # Functionality for receiving info about all badges (either all badges that exist or just all the ones owned by the current user)
    isUserBadges : bool = True if request.form.get("user_assigned") else False

    if isUserBadges:
        badge_list = current_user.badges       # Badges.query.filter_by(user_id=current_user.id).all()
    else:
        badge_list = Badges.query.all()

    output_list = []

    for badge in badge_list:
        output_list.append({
            "id" : badge.id,
            "name" : badge.name,
            "description" : badge.description,
            "points_req" : badge.points_threshold
        })

    return jsonify(output_list), 200

# Route for one specific badge (related to the current logged in user) 
@routes.route("/user_badge", methods=["POST", "DELETE"])
@login_required
def modify_user_badges():
    # Not sure whether if badge should be referred to by ID or name, so both options are provided for now 
    # (delete one later when decided); only one is necessary to filter the entry, and the other can be left out
    badge_ID : int = request.form.get("badge_id", None)     
    badge_name : str = request.form.get("badge_name", None)

    match (request.method):
        case "POST":
            # Functionality for updating/appending to badge info
            print(f"Debug Badge before: {current_user.badges}")

            badge = Badges.query.filter(or_(Badges.id==badge_ID, Badges.name==badge_name)).first_or_404()

            if badge not in current_user.badges:
                current_user.badges.append(badge)

            db.session.commit()
            
            print(f"Debug Badge after: {current_user.badges}")

            return "Success!", 201

        case "DELETE":
            # Functionality for removing badge from user (for whatever reason...)
            print(f"Debug Badge before: {current_user.badges}")

            badge = Badges.query.filter(or_(Badges.id==badge_ID, Badges.name==badge_name)).first_or_404()

            if badge in current_user.badges:
                current_user.badges.remove(badge)

            db.session.commit()
            
            print(f"Debug Badge after: {current_user.badges}")

            return "Successfully removed badge from user!", 201
        
        case _:
            return "400: Bad request", 400

# Route related to a collection of achievements
@routes.route("/achievements", methods=["GET"])
@login_required
def get_achieve():
    # Functionality for receiving achievements info (either all that exist, or just all the ones earned by the current user)
    isUserAchieve : bool = True if request.form.get("user_assigned") else False

    if isUserAchieve:
        achieve_list = current_user.achievements       # Achievements.query.filter_by(user_id=current_user.id).all()
    else:
        achieve_list = Achievements.query.all()

    output_list = []

    for achieve in achieve_list:
        output_list.append({
            "id" : achieve.id,
            "name" : achieve.name,
            "description" : achieve.description,
            "points_req" : achieve.points_threshold
        })

    return jsonify(output_list)

# Route for one specific achievement (related to the current logged in user)    
@routes.route("/user_achievement", methods=["POST", "DELETE"])       # Should PUT be used here instead of POST?
@login_required
def change_user_achieve():
    # Not sure whether if achievement should be referred to by ID or name, so both options are provided for now 
    # (delete one later when decided); only one is necessary to filter the entry, and the other can be left out
    achieve_ID : int = request.form.get("achievement_id", None)     
    achieve_name : str = request.form.get("achievement_name", None)

    match (request.method):
        case "POST":
            # Functionality for updating/appending to achievement info
            print(f"Debug achievement before: {current_user.achievements}")

            achieve = Achievements.query.filter(or_(Achievements.id==achieve_ID, Achievements.name==achieve_name)).first_or_404()

            if achieve not in current_user.achievements:
                current_user.achievements.append(achieve)

            db.session.commit()
            
            print(f"Debug achievement after: {current_user.achievements}")

            return "Success!", 201
        
        case "DELETE":
            # Functionality for removing achievement from user (for whatever reason...)
            print(f"Debug achievement before: {current_user.achievements}")

            achieve_ID = request.form.get("achievement_id")        
            achieve_name = request.form.get("achievement_name")
            achieve = Achievements.query.filter(or_(Achievements.id==achieve_ID, Achievements.name==achieve_name)).first_or_404()

            if achieve in current_user.achievements:
                current_user.achievements.remove(achieve)

            db.session.commit()
            
            print(f"Debug achievement after: {current_user.achievements}")

            return "Success!", 201
        
        case _:
            return "400: Bad request", 400

# Route pertaining to getting/changing current logged in user's points count
@routes.route("/user_points", methods=["GET", "POST"])
@login_required
def change_user_points():
    # This is for the POST request; not necessary to include for the GET request
    points : int = request.form.get("num_points", default=0)

    match (request.method):
        case "POST":
            # Functionality for modifying user points info in the database
            points_obj = current_user.points       # Points.query.filter_by(user_id=current_user.id).first()

            if points_obj == None:
                points_obj = Points(points=points, user=current_user)
                current_user.points = points_obj         # Not sure if this is necessary
                db.session.add(points_obj)
            else:
                points_obj.points = points

            db.session.commit()

            return "Successfully registered current user's points!", 201
        case "GET":
            # Functionality for receiving a user's points info
            points = current_user.points           # Points.query.filter_by(user_id=current_user.id).first()

            return points, 200
        
        case _:
            return "400: Bad request", 400
        
# Route related to a collection of quizzes        
@routes.route("/quizzes", methods=["GET"])   
@login_required
def get_quizzes():
    """
    General format and typing of returned JSON object for a single quiz, for reference:
    {
        "id" : Integer,
        "title" : String,
        "subject_type" : String value from Subject(Enum),
        "start_time" : String in 'YYYY-MM-DD hh:mm:ss' format,
        "end_time" : String in 'YYYY-MM-DD hh:mm:ss' format,
        "is_active" : Boolean,
        "level" : Integer,
        "score" : Integer,
        "questions" : [
            {
                "question_id" : Integer,
                "question_content" : String,
                "question_answers" : [
                    {
                        "answer_id" : Integer, 
                        "answer_content" : String, 
                        "answer_correct" : Boolean
                    }
                ]
            }
        ]
    }
    """
    # Functionality for receiving info on all available quizzes
    isUserQuiz : bool = True if request.form.get("user_assigned") else False

    # Filter quizzes by user or obtain all existing quizzes (based on request form data)
    if isUserQuiz:
        quiz_list = current_user.quizzes       # Quiz.query.filter_by(user_id=current_user.id).all()
    else:
        quiz_list = Quiz.query.all()

    output_list = []

    # Compile all quizzes into JSON format specified above within a list
    for quiz in quiz_list:
        # quiz = Quiz.query.filter(and_(Quiz.users.any(User.id == current_user.id), Quiz.id == quiz_ID)).first_or_404()
        
        quiz_questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
        quiz_answers = QuizAnswer.query.filter_by(quiz_id=quiz.id).all()
        
        quiz_q_output = [{ "question_id" : question.id, 
                        "question_content" : question.question_content} for question in quiz_questions]
        
        for question in quiz_q_output:
            related_answers = [answer for answer in quiz_answers if (answer.quiz_question_id == question["question_id"])]
            quiz_a_output = [{"answer_id" : answer.id, 
                            "answer_content" : answer.answer_content, 
                            "answer_correct" : answer.correct} for answer in related_answers]
            
            question["question_answers"] = quiz_a_output

        outputQuiz = {
            "id" : quiz.id,        
            "title" : quiz.title,
            "subject_type" : quiz.subject_type.value,
            "start_time" : str(quiz.start_time),
            "end_time" : str(quiz.end_time),
            "is_active" : quiz.active,
            "level" : quiz.level,
            "score" : quiz.score,
            "questions" : quiz_q_output
        }

        output_list.append(outputQuiz)

    return jsonify(output_list), 200
    
# Route for one specific quiz (related to the current logged in user)    
@routes.route("/user_quiz", methods=["POST", "DELETE"])   # Should PUT be used here instead of POST?
@login_required
def modify_user_quiz():
    quiz_ID : int = request.form.get("quiz_id")

    match (request.method):
        case "POST":
            # Functionality to add a user to a preexisting quiz
            quiz = Quiz.query.filter_by(id=quiz_ID).first_or_404()
            current_user.quizzes.append(quiz)

            db.session.commit()
            return "Successfully added user to quiz!", 201
        
        case "DELETE":
            # Functionality to remove a user from a preexisting quiz
            quiz = Quiz.query.filter(and_(Quiz.users.any(User.id == current_user.id), Quiz.id == quiz_ID)).first_or_404()
            quiz.users.remove(current_user)

            db.session.commit()

            return "Successfully removed user from quiz!", 201
        
        case _:
            return "400: Bad request", 400

# Route related to a collection of lessons
@routes.route("/lessons", methods=["GET"])
@login_required
def get_lessons():
    """
    General format and typing of returned JSON object for a single lesson, for reference:
    {
        "id" : Integer,
        "title" : String,
        "subject_type" : String value from Subject(Enum),
        "start_time" : String in 'YYYY-MM-DD hh:mm:ss' format,
        "end_time" : String in 'YYYY-MM-DD hh:mm:ss' format,
        "level" : Integer,
        "active" : Boolean,
        "summary" : String,
        "learning_objective" : String,
        "lesson_content" : String
    }
    """

    # Functionality for receiving info on all available lessons
    isUserLesson : bool = True if request.form.get("user_assigned") else False

    # Filter lessons by user or obtain all lessons (based on request form data)
    if isUserLesson:
        lesson_list = current_user.lessons       # Lesson.query.filter_by(user_id=current_user.id).all()
    else:
        lesson_list = Lesson.query.all()

    output_list = []

    # Compile all lessons into JSON format specified above within a list
    for lesson in lesson_list:
        # lesson = Lesson.query.filter(and_(Lesson.users.any(User.id == current_user.id), Lesson.id == lesson_ID)).first_or_404()
        
        outputLesson = {
            "id" : lesson.id,
            "title" : lesson.title,
            "subject_type" : lesson.subject_type.value,
            "start_time" : str(lesson.start_time),
            "end_time" : str(lesson.end_time),
            "level" : lesson.level,
            "active" : lesson.active,
            "summary" : lesson.summary,
            "objective" : lesson.learning_objective,
            "lesson_content" : lesson.lesson_content 
        }

        output_list.append(outputLesson)

    return jsonify(output_list), 200

# Route for one specific lesson (related to the current logged in user)
@routes.route("/user_lesson", methods=["POST", "DELETE"])
@login_required
def modify_user_lesson():
    lesson_ID : int = request.form.get("lesson_id")

    match (request.method):
        case "POST":
            # Functionality to add a user to a preexisting lesson
            lesson = Lesson.query.filter_by(id=lesson_ID).first_or_404()
            current_user.lessons.append(lesson)

            db.session.commit()
            return "Successfully added user to lesson!", 201
        
        case "DELETE":
            # Functionality to remove a user from a preexisting lesson
            lesson = Lesson.query.filter(and_(Lesson.users.any(User.id == current_user.id), Lesson.id == lesson_ID)).first_or_404()
            lesson.users.remove(current_user)

            db.session.commit()

            return "Successfully removed user from lesson!", 201
        
        case _:
            return "400: Bad request", 400