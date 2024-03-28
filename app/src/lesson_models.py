from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, func, ForeignKey
from datetime import datetime, timezone, timedelta
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

bcrypt = Bcrypt()
les_db = SQLAlchemy()

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

user_course = les_db.Table(
    'user_course',
    les_db.Column('user_id', les_db.Integer, ForeignKey('user.id'), primary_key=True),
    les_db.Column('course_id', les_db.Integer, ForeignKey('course.id'), primary_key=True)
)

user_module = les_db.Table(
    'user_module',
    les_db.Column('user_id', les_db.Integer, ForeignKey('user.id'), primary_key=True),
    les_db.Column('module_id', les_db.Integer, ForeignKey('module.id'), primary_key=True)
)

user_topic = les_db.Table(
    'user_topic',
    les_db.Column('user_id', les_db.Integer, ForeignKey('user.id'), primary_key=True),
    les_db.Column('topic_id', les_db.Integer, ForeignKey('topic.id'), primary_key=True)
)

teacher_course = les_db.Table(
    'teacher_course',
    les_db.Column('teacher_id', les_db.Integer, ForeignKey('teacher.id'), primary_key=True),
    les_db.Column('course_id', les_db.Integer, ForeignKey('course.id'), primary_key=True)
)

teacher_module = les_db.Table(
    'teacher_module',
    les_db.Column('teacher_id', les_db.Integer, ForeignKey('teacher.id'), primary_key=True),
    les_db.Column('module_id', les_db.Integer, ForeignKey('module.id'), primary_key=True)
)

teacher_topic = les_db.Table(
    'teacher_topic',
    les_db.Column('teacher_id', les_db.Integer, ForeignKey('teacher.id'), primary_key=True),
    les_db.Column('topic_id', les_db.Integer, ForeignKey('topic.id'), primary_key=True)
)

teacher_student = les_db.Table(
    'teacher_student',
    les_db.Column('teacher_id', les_db.Integer, ForeignKey('teacher.id'), primary_key=True),
    les_db.Column('student_id', les_db.Integer, ForeignKey('user.id'), primary_key=True)
)


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


user_quiz = les_db.Table(
    'user_quiz',
    les_db.Column('user_id', les_db.Integer, ForeignKey('user.id'), primary_key=True),
    les_db.Column('quiz_id', les_db.Integer, ForeignKey('quiz.id'), primary_key=True)
)

user_lesson = les_db.Table(
    'user_lesson',
    les_db.Column('user_id', les_db.Integer, ForeignKey('user.id'), primary_key=True),
    les_db.Column('lesson_id', les_db.Integer, ForeignKey('lesson.id'), primary_key=True)
)

teacher_quiz = les_db.Table(
    'teacher_quiz',
    les_db.Column('teacher_id', les_db.Integer, ForeignKey('teacher.id'), primary_key=True),
    les_db.Column('quiz_id', les_db.Integer, ForeignKey('quiz.id'), primary_key=True)
)

teacher_lesson = les_db.Table(
    'teacher_lesson',
    les_db.Column('teacher_id', les_db.Integer, ForeignKey('teacher.id'), primary_key=True),
    les_db.Column('lesson_id', les_db.Integer, ForeignKey('lesson.id'), primary_key=True)
)


class Course(les_db.Model):
    id = les_db.Column(les_db.Integer, primary_key=True)
    name = les_db.Column(les_db.String(100), nullable=False)
    subject_type = les_db.Column(SQLAlchemyEnum(Subject), nullable=False)
    modules = les_db.relationship('Module', backref='course', lazy='dynamic')
    # users = les_db.relationship('User', secondary=user_course, backref='courses', lazy='dynamic')
    # teacher = les_db.relationship('Teacher', secondary=teacher_course, backref='courses', lazy='dynamic')
    # ^^ Relationships defined so that each course can have many modules, and be accessed by many users

class Module(les_db.Model):
    id = les_db.Column(les_db.Integer, primary_key=True)
    name = les_db.Column(les_db.String(100), nullable=False)
    course_id = les_db.Column(les_db.Integer, ForeignKey('course.id'), nullable=False)
    topics = les_db.relationship('Topic', backref='module', lazy='dynamic')
    # users = les_db.relationship('User', secondary=user_module, backref='modules', lazy='dynamic')
    # teacher = les_db.relationship('Teacher', secondary=teacher_module, backref='modules', lazy='dynamic')
    # ^^ Relationships defined so that each module can have many topics, and be accessed by many users

class Topic(les_db.Model):
    id = les_db.Column(les_db.Integer, primary_key=True)
    name = les_db.Column(les_db.String(100), nullable=False)
    module_id = les_db.Column(les_db.Integer, ForeignKey('module.id'), nullable=False)
    quiz_id = les_db.Column(les_db.Integer, ForeignKey('quiz.id'), nullable=True)
    lesson_id = les_db.Column(les_db.Integer, ForeignKey('lesson.id'), nullable=True)
    # users = les_db.relationship('User', secondary=user_topic, backref='topics', lazy='dynamic')
    # teacher = les_db.relationship('Teacher', secondary=teacher_topic, backref='topics', lazy='dynamic')
    # ^^^ Relationships defined so that each topic has a unique lesson and unique quiz, and can be accessed by many users.


class Activity(les_db.Model):
    id = les_db.Column(les_db.Integer, primary_key=True)
    title = les_db.Column(les_db.String(100), nullable=False)
    # user_id = les_db.Column(les_db.Integer, ForeignKey('user.id'), nullable=False)
    subject_type = les_db.Column(SQLAlchemyEnum(Subject), nullable=False, default=Subject.BIOLOGY)
    start_time = les_db.Column(les_db.DateTime, nullable=True, default=func.now()) 
    end_time = les_db.Column(les_db.DateTime, nullable=True, default=func.now())
    activity_type = les_db.Column(SQLAlchemyEnum(ActivityType), nullable=False)   # Took out: default=ActivityType.LESSON

    __mapper_args__ = {
        "polymorphic_on": activity_type,   
        "polymorphic_identity": ActivityType.ACTIVITY
    }
        
# Lesson
class Lesson(Activity):
    id = les_db.Column(les_db.Integer, les_db.ForeignKey('activity.id'), primary_key=True)
    # level = les_db.Column(les_db.Integer, nullable=False)  # how difficult is the lesson (easy=1, medium=2, hard=3)
    # active = les_db.Column(les_db.Boolean, nullable=False) # determine whether the lesson is submitted or not
    # summary = les_db.Column(les_db.Text, nullable=False)   # lesson summary
    learning_objective = les_db.Column(les_db.Text, nullable=False)
    lesson_content = les_db.Column(les_db.Text)
    video_filename = les_db.Column(les_db.String(255))
    thumbnail_filename = les_db.Column(les_db.String(255))
    textbook_name = les_db.Column(les_db.String(255))
    textbook_pages = les_db.Column(les_db.Text)
    practice_content = les_db.Column(les_db.Text)
    users = les_db.relationship('User', secondary=user_lesson, backref='lessons')
    teacher = les_db.relationship('Teacher', secondary=teacher_lesson, backref='lessons')
    topic_id = les_db.Column(les_db.Integer, ForeignKey('topic.id'), nullable=True)
    # ^ Establish relationship where each unique lesson is a part of a single topic.

    __mapper_args__ = {
        "polymorphic_identity": ActivityType.LESSON
    }

# Quiz Table
class Quiz(Activity):
    id = les_db.Column(les_db.Integer, les_db.ForeignKey('activity.id'), primary_key=True)
    active = les_db.Column(les_db.Boolean, nullable=False) # determine whether the quiz is submitted or not
    level = les_db.Column(les_db.Integer, nullable=False)  # how difficult is the quiz (easy=1, medium=2, hard=3)
    score = les_db.Column(les_db.Integer, nullable=False)  # quiz score
    users = les_db.relationship('User', secondary=user_quiz, backref='quizzes')
    teacher = les_db.relationship('Teacher', secondary=teacher_quiz, backref='quizzes')
    topic_id = les_db.Column(les_db.Integer, les_db.ForeignKey('topic.id'), nullable=True)
    # ^ Establish relationship where each unique quiz is a part of a single topic.

    __mapper_args__ = {
        "polymorphic_identity": ActivityType.QUIZ
    }

# Quiz Questions
class QuizQuestion(les_db.Model):
    id = les_db.Column(les_db.Integer, primary_key=True) # id for identify quiz question
    quiz_id = les_db.Column(les_db.Integer, les_db.ForeignKey('quiz.id'), nullable=False) # identify which quiz the question belongs to
    question_content = les_db.Column(les_db.Text, nullable=False)

# Quiz Answers
class QuizAnswer(les_db.Model):
    id = les_db.Column(les_db.Integer, primary_key=True)
    quiz_id = les_db.Column(les_db.Integer, les_db.ForeignKey('quiz.id'), nullable=False) # identify which quiz the answer belongs to
    quiz_question_id = les_db.Column(les_db.Integer, les_db.ForeignKey('quiz_question.id'), nullable=False) # identify which quiz question the answer belongs to
    correct = les_db.Column(les_db.Boolean, nullable=False)
    answer_content = les_db.Column(les_db.Text, nullable=False)
