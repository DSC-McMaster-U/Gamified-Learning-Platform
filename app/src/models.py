from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, func
from datetime import datetime, timezone, timedelta
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

bcrypt = Bcrypt()
db = SQLAlchemy()

# Predefined grade selections
# Note: when adding a new user, use "grade=GradeEnum.NINTH" to assign a grade (in this example, 9th grade)
class GradeEnum(Enum):
    FIRST = '1st Grade'
    SECOND = '2nd Grade'
    THIRD = '3rd Grade'
    FOURTH = '4th Grade'
    FIFTH = '5th Grade'
    SIXTH = '6th Grade'
    SEVENTH = '7th Grade'
    EIGHTH = '8th Grade'
    NINTH = '9th Grade'
    TENTH = '10th Grade'
    ELEVENTH = '11th Grade'
    TWELFTH = '12th Grade'
    FRESHMAN = 'University Freshman'
    SOPHMORE = 'University Sophmore'
    JUNIOR = 'University Junior'
    SENIOR = 'University Senior'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(40), unique=True, nullable=False)
    hashed_password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer, CheckConstraint('age >= 0 AND age <= 100', name='check_age_range'))
    grade = db.Column(SQLAlchemyEnum(GradeEnum), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.now(timezone(timedelta(hours=-5))))
    favorite_subject = db.Column(db.String(50))
    failed_signin_attempts = db.Column(db.Integer, default=0)
    
    # Set user password
    def set_password(self, password):
        self.hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Check if entered password is correct
    def check_password(self, password):
        return bcrypt.check_password_hash(self.hashed_password, password)

# Points Progress
class Points(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # establish relationship between 'points' and 'user' model, indicates the points are associated w/ a specific user 
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, default=0)

# Quiz vs. Task
class ActivityType(Enum):
    TASK='Task'
    QUIZ='Quiz'

class Subject(Enum):
    CALCULUS='Calculus'
    LINALG='Linear Algebra'
    BIOLOGY='Biology'
    CHEMISTRY='Chemistry'
    PHYSICS='Physics'
    ENGLISH='English'
    FRENCH='French'
    COMSCI='Computer Science'
    # ... add/take away as needed

# Quizzes/Tasks
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # establish relationship between 'quiz' and 'user' model
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(SQLAlchemyEnum(ActivityType), nullable=False, default=ActivityType.TASK)
    subject_type = db.Column(SQLAlchemyEnum(Subject), nullable=False, default=Subject.BIOLOGY)
    start_time = db.Column(db.DateTime, nullable=True, default=func.now()) 
    end_time = db.Column(db.DateTime, nullable=True, default=func.now())
    score = db.Column(db.Float, nullable=False)
    
    if activity_type == ActivityType.QUIZ:
        questions = db.relationship('QuizQuestion', backref='activity', lazy=True, cascade='all, delete-orphan', 
                                primaryjoin="and_(Activity.id == QuizQuestion.activity_id, Activity.activity_type == 'QUIZ')")
    elif activity_type == ActivityType.TASK:
        questions = db.relationship('TaskQuestion', backref='task', lazy=True, cascade='all, delete-orphan', 
                                primaryjoin="and_(Activity.id == TaskQuestion.activity_id, Activity.activity_type == 'TASK')")
        

# Quiz Questions
class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True) # id for identify quiz question
    quiz_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False) # how difficult is the question (easy, medium, hard)
    active = db.Column(db.Boolean, nullable=False) # determine whether the question is submitted or not
    score = db.Column(db.Integer, nullable=False) # score for that question
    question_content = db.Column(db.Text, nullable=False)

# Task Questions
class TaskQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True) # id for identifying task question
    task_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False) # id for identifying parent task
    level = db.Column(db.Integer, nullable=False) # how difficult is the question (easy, medium, hard)
    active = db.Column(db.Boolean, nullable=False) # determine whether the question is submitted or not
    score = db.Column(db.Integer, nullable=False) # score for that question
    question_content = db.Column(db.Text, nullable=False)

# Quiz Answers
class QuizAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False) # id to identify with parent quiz
    quiz_question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), nullable=False) # id to identify quiz question
    correct = db.Column(db.Boolean, nullable=False)
    answer_content = db.Column(db.Text, nullable=False)

# Task Answers
class TaskAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False) # id to identify with parent task
    task_question_id = db.Column(db.Integer, db.ForeignKey('task_question.id'), nullable=False) # id to identify task question
    correct = db.Column(db.Boolean, nullable=False)
    answer_content = db.Column(db.Text, nullable=False)