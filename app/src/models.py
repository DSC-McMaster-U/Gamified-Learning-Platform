from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, func, ForeignKey
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
    SOPHOMORE = 'University Sophomore'
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
    age = db.Column(db.Integer)
    grade = db.Column(SQLAlchemyEnum(GradeEnum), default=GradeEnum.NA, nullable=True)
    registration_date = db.Column(db.DateTime, default=datetime.now(timezone(timedelta(hours=-5))))
    favorite_subject = db.Column(db.String(50), nullable=True)
    failed_signin_attempts = db.Column(db.Integer, default=0)
    points = db.relationship('Points', uselist=False, backref='user') # establish one-to-one relationship between 'points' and 'user' model
    streak = db.Column(db.Integer, default=0)
    
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
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False, unique=True)
    points = db.Column(db.Integer, default=0)
    # user = db.relationship('User', uselist=False, backref='points')

# Helper table to join User and Badges into many-to-many relationship
user_badge = db.Table(
    'user_badge',
    db.Column('user_id', db.Integer, ForeignKey('user.id'), nullable=False),
    db.Column('badge_id', db.Integer, ForeignKey('badges.id'), nullable=False)
)

# Helper table to join User and Achievements into many-to-many relationship
user_achieve = db.Table(
    'user_achieve',
    db.Column('user_id', db.Integer, ForeignKey('user.id'), nullable=False),
    db.Column('achievement_id', db.Integer, ForeignKey('achievements.id'), nullable=False)
)

class Badges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # name of the badge
    description = db.Column(db.Text, nullable=False) # description of the badge
    points_threshold = db.Column(db.Integer, nullable=False) # points required to earn a badge
    # user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False) # create relationship between user and badge earned
    users = db.relationship('User', secondary=user_badge, backref='badges')  # establish relationship with the User table

class Achievements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    points_threshold = db.Column(db.Integer, nullable=False) # points required to earn an achievement
    # user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False) # create relationship between user and achievement earned
    users = db.relationship('User', secondary=user_achieve, backref='achievements') # establish relationship with the User table


# Quiz vs. Task
class ActivityType(Enum):
    ACTIVITY='Activity'   # General activity type; required for polymorphic identity arg. in constructor
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
    COMPSCI='Computer Science'
    # ... add/take away as needed

"""
Helper tables to join User and Quiz/Lessons into a many-to-many relationship
Explanation: Before, unique activities would have to be created for each individual user, and
             only one user can be assigned to an activity, while a user can have multiple activities.
             But what if there's one universal activity where multiple users are assigned to? Creating 
             multiple unique activity entries with the same values will take up unnecessary space, and it would 
             be a bit annoying to find all users taking that universal activity.
             
             Therefore, if there's a many-to-many relationship instead between users and activities, you
             can just have one unique activity which has multiple different users assigned to it (keeping track
             with a users list), but one user can have multiple different quizzes they are assigned to (keeping
             track per user with their own quizzes list).
"""
user_quiz = db.Table(
    'user_quiz',
    db.Column('user_id', db.Integer, ForeignKey('user.id'), nullable=False),
    db.Column('quiz_id', db.Integer, ForeignKey('quiz.id'), nullable=False)
)

user_lesson = db.Table(
    'user_lesson',
    db.Column('user_id', db.Integer, ForeignKey('user.id'), nullable=False),
    db.Column('lesson_id', db.Integer, ForeignKey('lesson.id'), nullable=False)
)

""" Notes/info about changes to old model:
This overall Activity module has two subclasses for quizzes and lessons, which inherits the general elements
from the Activity class (joined table inheritance). Based on what subclass it is, the activity_type from the superclass 
will change accordingly to either ActivityType.LESSON or ActivityType.QUIZ depending on the subclass, or just
a general ActivityType.ACTIVITY value if just creating an Activity superclass object (which, realistically, should never 
happen). This is indicated by the __mapper_args__ constructor, which establishes the polymorphic relationship between 
the classes and sets a discriminator value upon instantiation to differentiate the classes' identities.

Lessons and quiz ID fields will be numbered as Activity ID fields, so querying by Activity.id could either
bring up a general Activity object or more unique Lesson and/or Quiz objects.

Besides the previous model's bugs with 'questions', this model is better than the previous conditional 
statement one as it gets rid of some redundant table columns and innately satisfies the primaryjoin conditions 
set. Quizzes & Lessons will always have their associated ActivityType value in activity_type, and their regular IDs will 
be synced through a foreign key (there's no need to have two separate Activity and Quiz/Lesson objects with 
separate IDs).

Note that due to the lack of a relationship with the User class, it might be best not to create a new
general Activity class; instead, just stick to instantiating Quizzes and Lessons, which have a many-to-many
relationship with Users. ...Maybe this schema can be revised in the future for Activities to have a relationship 
with users?
"""
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # establish relationship between 'quiz' and 'user' model
    # user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    subject_type = db.Column(SQLAlchemyEnum(Subject), nullable=False, default=Subject.BIOLOGY)
    start_time = db.Column(db.DateTime, nullable=True, default=func.now()) 
    end_time = db.Column(db.DateTime, nullable=True, default=func.now())
    activity_type = db.Column(SQLAlchemyEnum(ActivityType), nullable=False)   # Took out: default=ActivityType.LESSON

    __mapper_args__ = {
        "polymorphic_on": activity_type,   
        "polymorphic_identity": ActivityType.ACTIVITY
    }
        
# Lesson
class Lesson(Activity):  # used to be db.Model arg
    # Changed id so that lessons use the same ID as Activities (since Lesson is one child of class Activities)
    id = db.Column(db.Integer, db.ForeignKey('activity.id'), primary_key=True)
    
    # id = db.Column(db.Integer, primary_key=True) # id for identifying lesson
    # activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False) # id for identifying parent lesson, establish relationship with Activity table
    level = db.Column(db.Integer, nullable=False)  # how difficult is the question (easy, medium, hard)
    active = db.Column(db.Boolean, nullable=False) # determine whether the lesson is submitted or not
    summary = db.Column(db.Text, nullable=False)   # lesson summary
    learning_objective = db.Column(db.Text, nullable=False)
    lesson_content = db.Column(db.Text, nullable=False)
    users = db.relationship('User', secondary=user_lesson, backref='lessons')

    __mapper_args__ = {
        "polymorphic_identity": ActivityType.LESSON
    }

# Quiz Table
class Quiz(Activity):    # used to be db.Model arg
    # Changed id so that quizzes use the same ID as Activities (since Quiz is one child of class Activities)
    id = db.Column(db.Integer, db.ForeignKey('activity.id'), primary_key=True)

    # id = db.Column(db.Integer, primary_key=True)
    # activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False) # determine whether the question is submitted or not
    level = db.Column(db.Integer, nullable=False)  # how difficult is the question (easy, medium, hard)
    score = db.Column(db.Integer, nullable=False)  # score for that question
    users = db.relationship('User', secondary=user_quiz, backref='quizzes')

    __mapper_args__ = {
        "polymorphic_identity": ActivityType.QUIZ
    }

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
