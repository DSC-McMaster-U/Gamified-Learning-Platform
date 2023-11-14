from .models import *
from sqlalchemy import and_

def testDB():
    db.drop_all()
    db.create_all()

    # Badge/Achievement testing
    user1 = User(
        name="A",
        username="Aa",
        hashed_password="Something",
        email="Something0",
        age=18,
        favorite_subject="Math",
    )
    user2 = User(
        name="A",
        username="Ab",
        hashed_password="Something",
        email="Something1",
        age=18,
        favorite_subject="Math",
    )
    user3 = User(
        name="A",
        username="Ac",
        hashed_password="Something",
        email="Something2",
        age=18,
        favorite_subject="Math",
    )

    badge1 = Achievements(
        name="B1",
        description="Badge",
        points_threshold=0,
    )

    badge2 = Achievements(
        name="B2",
        description="Badge",
        points_threshold=0,
    )

    badge1.users.append(user1)
    badge1.users.append(user2)

    # badge1.user.append(user1, user2, user3)
    db.session.add_all([user1, user2, user3])
    db.session.add_all([badge1, badge2])
    db.session.commit()

    test = Achievements.query.filter_by(name="B1").first()
    print('TITLE: ', test.name)
    print('-')
    print('Users:')
    print(test.users)
    for user in test.users:
        print('> ', user.name)

    print(user1.achievements)
    print("--------")
    print(f"Points before: {user1.points}")

    # Points testing
    points = 5
    points_obj = user1.points # Points.query.filter_by(user_id=current_user.id).first()

    if points_obj == None or points_obj == []:
        points_obj = Points(points=points, user=user1)
        db.session.add(points_obj)
        user1.points = points_obj         # Not sure if this is necessary

    else:
        points_obj.points = points

    db.session.commit()

    print(f"Points after: {user1.points.points}")
    print(points_obj.user)

    print("--------")
    # Quiz Testing
    quiz1 = Quiz(
        title="Quiz 1",
        subject_type=Subject.CALCULUS,

        active=False,
        level=1,
        score=50        
    )

    quiz2 = Quiz(
        title="Quiz 2",
        subject_type=Subject.BIOLOGY,

        active=True,
        level=3,
        score=20       
    )

    quiz1.users.append(user1)

    db.session.add_all([quiz1, quiz2])
    db.session.commit()

    quizQ1 = QuizQuestion(
        quiz_id = quiz1.id,
        question_content = "This is a question."
    )

    quizQ2 = QuizQuestion(
        quiz_id = quiz2.id,
        question_content = "Quiz 2 Question"
    )

    db.session.add_all([quizQ1, quizQ2])
    db.session.commit()

    quizA1 = QuizAnswer(
        quiz_id = quiz1.id,
        quiz_question_id = quizQ1.id,
        correct = True,
        answer_content = "This is the first answer to Question 1."
    )

    quizA2 = QuizAnswer(
        quiz_id = quiz1.id,
        quiz_question_id = quizQ1.id,
        correct = False,
        answer_content = "This is the second answer to Question 1."
    )

    quizA3 = QuizAnswer(
        quiz_id = quiz2.id,
        quiz_question_id = quizQ2.id,
        correct = True,
        answer_content = "This is the first answer to Question 2."
    )

    db.session.add_all([quizA1, quizA2, quizA3])

    # db.session.add_all([act1, quiz1, quizQ1, quizA1])
    db.session.commit()
    
    # Functionality for receiving info on all available lessons
    isUserQuiz : bool = False

    # Filter quizzes by user1 or obtain all quizzes
    if isUserQuiz:
        quiz_list = user1.quizzes
    else:
        quiz_list = Quiz.query.all()

    output = []

    # quiz = Quiz.query.filter(and_(Quiz.users.any(User.id == user1.id), Quiz.id == quiz1.id)).first_or_404()
    print(quiz_list)

    for quiz in quiz_list:

        quiz_questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
        quiz_answers = QuizAnswer.query.filter_by(quiz_id=quiz.id).all()
        
        quiz_q_output = [{ "question_id" : question.id, 
                        "question_content" : question.question_content} for question in quiz_questions]
        
        print(quiz_questions)
        print(quiz_answers)

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

        output.append(outputQuiz)

    print(output)
    print("----------")

    # Test functionality to add a user to a preexisting quiz
    print("Testing adding quiz2 to user1: ")
    quiz_ID = quiz2.id

    quiz = Quiz.query.filter_by(id=quiz_ID).first_or_404()
    user1.quizzes.append(quiz)

    db.session.commit()
    
    print(user1.quizzes)
    print("----------")

    # Test functionality to remove a user from a preexisting quiz
    print("Testing removing quiz1 from user1: ")
    quiz_ID = quiz1.id

    quiz = Quiz.query.filter(and_(Quiz.users.any(User.id == user1.id), Quiz.id == quiz_ID)).first_or_404()
    quiz.users.remove(user1)

    db.session.commit()

    print(user1.quizzes)
    print("----------")

    db.session.delete(badge1)
    db.session.delete(badge2)
    db.session.delete(user1)
    db.session.delete(user2)
    db.session.delete(user3)
    db.session.delete(points_obj)
    db.session.delete(quiz1)
    db.session.delete(quizQ1)
    db.session.delete(quizA1)
    db.session.commit()

