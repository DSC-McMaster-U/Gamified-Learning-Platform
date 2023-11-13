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
    NA = 'Not Available'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(40), unique=True, nullable=False)
    hashed_password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer, CheckConstraint('age >= 0 AND age <= 100', name='check_age_range'))
    grade = db.Column(SQLAlchemyEnum(GradeEnum), default=GradeEnum.NA)
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
    user = db.relationship('User', backref='points')

class Badges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # name of the badge
    description = db.Column(db.Text, nullable=False) # description of the badge
    points_threshold = db.Column(db.Integer, nullable=False) # points required to earn a badge
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False) # create relationship between user and badge earned
    user = db.relationship('User', backref='badges')  # establish relationship with the User table

class Achievements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    points_threshold = db.Column(db.Integer, nullable=False) # points required to earn an achievement
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False) # create relationship between user and achievement earned
    user = db.relationship('User', backref='achievements') # establish relationship with the User table


# Quiz vs. Task
class ActivityType(Enum):
    LESSON='Lesson'
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

# The overall module, contains common attributes between lessons and quizzes
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # establish relationship between 'quiz' and 'user' model
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(SQLAlchemyEnum(ActivityType), nullable=False, default=ActivityType.LESSON)
    subject_type = db.Column(SQLAlchemyEnum(Subject), nullable=False, default=Subject.BIOLOGY)
    start_time = db.Column(db.DateTime, nullable=True, default=func.now()) 
    end_time = db.Column(db.DateTime, nullable=True, default=func.now())
    
    # associating with activities based on activity_type
    if activity_type == ActivityType.QUIZ:
        # primaryjoin: specify the condition for the join. For quiz, the activity id and type has to be quiz 
        # backref: specify the name of the attribute that will be added to the 'Quiz' or 'Lesson' model. Each quiz instance will have an attribute 'activity' that refers to the related 'Activity' instance
        # lazy=True: controls when SQLAlchemy loads data from the databse. 'Quiz' and 'Lesson' objects will be loaded only when 'activity' attribute is accessed
        # cascade='all, delete-orphan': delete any orphaned child objects (no longer associated with a parent)
        questions = db.relationship('Quiz', backref='activity', lazy=True, cascade='all, delete-orphan', 
                                primaryjoin="and_(Activity.id == Quiz.activity_id, Activity.activity_type == 'QUIZ')")
    elif activity_type == ActivityType.LESSON:
        questions = db.relationship('Lesson', backref='task', lazy=True, cascade='all, delete-orphan', 
                                primaryjoin="and_(Activity.id == Lesson.activity_id, Activity.activity_type == 'LESSON')")
        
# Lesson
class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True) # id for identifying lesson
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False) # id for identifying parent lesson, establish relationship with Activity table
    level = db.Column(db.Integer, nullable=False) # how difficult is the question (easy, medium, hard)
    active = db.Column(db.Boolean, nullable=False) # determine whether the lesson is submitted or not
    summary = db.Column(db.Text, nullable=False) # lesson summary
    learning_objective = db.Column(db.Text, nullable=False)
    lesson_content = db.Column(db.Text, nullable=False)

# Quiz Table
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id', nullable=False))
    active = db.Column(db.Boolean, nullable=False) # determine whether the question is submitted or not
    level = db.Column(db.Integer, nullable=False) # how difficult is the question (easy, medium, hard)
    score = db.Column(db.Integer, nullable=False) # score for that question

# Quiz Questions
class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True) # id for identify quiz question
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False) # identify which quiz the question belongs to
    question_content = db.Column(db.Text, nullable=False)

# Quiz Answers
class QuizAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False) # identify which quiz the answer belongs to
    quiz_question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), nullable=False) # identify which quiz question the answer belongs to
    correct = db.Column(db.Boolean, nullable=False)
    answer_content = db.Column(db.Text, nullable=False)
