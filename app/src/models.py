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

"""
New Additions: 
The association tables 'user_course', 'user_module', and 'user_topic' are essential for establishing many-to-many 
relationships between users and the new models added to our educational platform: courses, modules, and topics.

user_course' connects users with courses, enabling the platform 
to handle scenarios where a user is enrolled in multiple courses, 
and a single course can have many users enrolled. This is crucial 
for tracking user enrollments and interactions at the course level.

'user_module' links users with modules, reflecting that 
users can engage with multiple modules within different courses, 
and each module can have numerous users. This association is key for
managing user progress and participation across various modules.

'user_topic' associates users with topics, allowing the platform to 
track which users are interacting with specific topics within modules. 
Since a user can engage with many topics, and each topic can be accessed 
by numerous users, this table facilitates the organization and retrieval 
of user-specific interactions at the topic level.

"""

user_course = db.Table(
    'user_course',
    db.Column('user_id', db.Integer, ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, ForeignKey('course.id'), primary_key=True)
)

user_module = db.Table(
    'user_module',
    db.Column('user_id', db.Integer, ForeignKey('user.id'), primary_key=True),
    db.Column('module_id', db.Integer, ForeignKey('module.id'), primary_key=True)
)

user_topic = db.Table(
    'user_topic',
    db.Column('user_id', db.Integer, ForeignKey('user.id'), primary_key=True),
    db.Column('topic_id', db.Integer, ForeignKey('topic.id'), primary_key=True)
)

'''
New Additions: 
The below association tables 'teacher_course', 'teacher_module', and 'teacher_topic' establish many-to-many 
relationships between teachers and the models added to our educational platform: courses, modules, and topics.
By doing so, we can enable mutiple teachers to collaborate on a course if needed.
'''

teacher_course = db.Table(
    'teacher_course',
    db.Column('teacher_id', db.Integer, ForeignKey('teacher.tid'), primary_key=True),
    db.Column('course_id', db.Integer, ForeignKey('course.id'), primary_key=True)
)

teacher_module = db.Table(
    'teacher_module',
    db.Column('teacher_id', db.Integer, ForeignKey('teacher.tid'), primary_key=True),
    db.Column('module_id', db.Integer, ForeignKey('module.id'), primary_key=True)
)

teacher_topic = db.Table(
    'teacher_topic',
    db.Column('teacher_id', db.Integer, ForeignKey('teacher.tid'), primary_key=True),
    db.Column('topic_id', db.Integer, ForeignKey('topic.id'), primary_key=True)
)

'''
New Additions: 
teacher_student establish a many-to-many between teachers and students. This way, we can easily manage teacher-student relationships
and allow teachers to view all of their students progress, or for students to have a centralized way to manage/interact with their teachers.
'''

teacher_student = db.Table(
    'teacher_student',
    db.Column('teacher_id', db.Integer, ForeignKey('teacher.tid'), primary_key=True),
    db.Column('student_id', db.Integer, ForeignKey('user.id'), primary_key=True)
)


class Teacher(UserMixin, db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(40), unique=True, nullable=False)
    hashed_password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer)
    registration_date = db.Column(db.DateTime, default=datetime.now(timezone(timedelta(hours=-5))))
    yrs_experience = db.Column(db.Integer, nullable=False)
    specialization = db.Column(db.String(50), nullable=True)
    # students = db.relationship('User', secondary=teacher_student, backref='teachers')
    courses = db.relationship('Course', secondary=teacher_course, backref='teachers')
    modules = db.relationship('Module', secondary=teacher_module, backref='teachers')
    topics = db.relationship('Topic', secondary=teacher_topic, backref='teachers')
        # Set teacher password
    def set_password(self, password):
        self.hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    # Check if entered password is correct
    def check_password(self, password):
        return bcrypt.check_password_hash(self.hashed_password, password)


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
    progress = db.relationship('UserProgress', back_populates='user', uselist=False)
    streak = db.Column(db.Integer, default=0)
    teachers = db.relationship('Teacher', secondary=teacher_student, backref='students')
    courses = db.relationship('Course', secondary=user_course, backref='users')
    modules = db.relationship('Module', secondary=user_module, backref='users')
    topics = db.relationship('Topic', secondary=user_topic, backref='users')
    # ^^^ Added new relationships between user and courses/modules/topics
    
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
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False, unique=True
    points = db.Column(db.Integer, default=0) # add index=True into points attribute to speed up points retrieval for queries?
    user = db.relationship('User', uselist=False, backref='points') 
    
    @classmethod
    def get_leaderboard(cls):
        return cls.query.order_by(cls.points.desc()).all()

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
    # users = db.relationship('User', secondary=user_badge, backref='badges')  # establish relationship with the User table

class Achievements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    points_threshold = db.Column(db.Integer, nullable=False) # points required to earn an achievement
    # user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False) # create relationship between user and achievement earned
    # users = db.relationship('User', secondary=user_achieve, backref='achievements') # establish relationship with the User table


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
    db.Column('user_id', db.Integer, ForeignKey('user.id'), primary_key=True),
    db.Column('quiz_id', db.Integer, ForeignKey('quiz.id'), primary_key=True)
)

user_lesson = db.Table(
    'user_lesson',
    db.Column('user_id', db.Integer, ForeignKey('user.id'), primary_key=True),
    db.Column('lesson_id', db.Integer, ForeignKey('lesson.id'), primary_key=True)
)

'''
New Additiions: 
The below association tables 'teacher_quiz', 'teacher_lesson', establish many-to-many 
relationships between teachers and the activities added to our educational platform: quizzes & lessons.
By doing so, we can track and enable mutiple teachers to collaborate on an activity if needed.
'''

teacher_quiz = db.Table(
    'teacher_quiz',
    db.Column('teacher_id', db.Integer, ForeignKey('teacher.tid'), primary_key=True),
    db.Column('quiz_id', db.Integer, ForeignKey('quiz.id'), primary_key=True)
)

teacher_lesson = db.Table(
    'teacher_lesson',
    db.Column('teacher_id', db.Integer, ForeignKey('teacher.tid'), primary_key=True),
    db.Column('lesson_id', db.Integer, ForeignKey('lesson.id'), primary_key=True)
)

"""
The addition of the Course, Module, and Topic models is crucial for expanding the structure of our educational platform. 
These models represent different levels of educational content organization, offering a hierarchical structure.

- Course Model: Represents the highest level of organization, representng a complete
course of study on a specific subject. Each course can contain multiple modules.
    Consider Calculus to be an example.

- Module Model: Serves as a subdivision within a course, focusing on specific areas or themes of the 
subject. This model enables the course content to be broken down into manageable and organized parts. 
    Consider the example of Derivatives as being a module within the calculus class.

- Topic Model: Topics are individual units of study within a module. Each topic is 
typically associated with specific activities like quizzes and lessons.
        Consider the example of Differentiation rules as being a topic within the Derivatives module.

"""

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_type = db.Column(SQLAlchemyEnum(Subject), nullable=False)
    modules = db.relationship('Module', backref='course', lazy='dynamic')
    # users = db.relationship('User', secondary=user_course, backref='courses', lazy='dynamic')
    # teacher = db.relationship('Teacher', secondary=teacher_course, backref='courses', lazy='dynamic')
    # ^^ Relationships defined so that each course can have many modules, and be accessed by many users

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, ForeignKey('course.id'), nullable=False)
    topics = db.relationship('Topic', backref='module', lazy='dynamic')
    # users = db.relationship('User', secondary=user_module, backref='modules', lazy='dynamic')
    # teacher = db.relationship('Teacher', secondary=teacher_module, backref='modules', lazy='dynamic')
    # ^^ Relationships defined so that each module can have many topics, and be accessed by many users

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    module_id = db.Column(db.Integer, ForeignKey('module.id'), nullable=False)
    quiz_id = db.Column(db.Integer, ForeignKey('quiz.id'), nullable=True)
    lesson_id = db.Column(db.Integer, ForeignKey('lesson.id'), nullable=True)
    # users = db.relationship('User', secondary=user_topic, backref='topics', lazy='dynamic')
    # teacher = db.relationship('Teacher', secondary=teacher_topic, backref='topics', lazy='dynamic')
    # ^^^ Relationships defined so that each topic has a unique lesson and unique quiz, and can be accessed by many users.


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
class Lesson(Activity):
    id = db.Column(db.Integer, db.ForeignKey('activity.id'), primary_key=True)
    level = db.Column(db.Integer, nullable=False)  # how difficult is the lesson (easy=1, medium=2, hard=3)
    active = db.Column(db.Boolean, nullable=False) # determine whether the lesson is submitted or not
    summary = db.Column(db.Text, nullable=False)   # lesson summary
    learning_objective = db.Column(db.Text, nullable=False)
    lesson_content = db.Column(db.Text, nullable=False)
    users = db.relationship('User', secondary=user_lesson, backref='lessons')
    teacher = db.relationship('Teacher', secondary=teacher_lesson, backref='lessons')
    topic_id = db.Column(db.Integer, ForeignKey('topic.id'), nullable=True)
    # ^ Establish relationship where each unique lesson is a part of a single topic.

    __mapper_args__ = {
        "polymorphic_identity": ActivityType.LESSON
    }

# Quiz Table
class Quiz(Activity):
    id = db.Column(db.Integer, db.ForeignKey('activity.id'), primary_key=True)
    active = db.Column(db.Boolean, nullable=False) # determine whether the quiz is submitted or not
    level = db.Column(db.Integer, nullable=False)  # how difficult is the quiz (easy=1, medium=2, hard=3)
    score = db.Column(db.Integer, nullable=False)  # quiz score
    users = db.relationship('User', secondary=user_quiz, backref='quizzes')
    teacher = db.relationship('Teacher', secondary=teacher_quiz, backref='quizzes')
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    # ^ Establish relationship where each unique quiz is a part of a single topic.

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

# User Progress to display on dashboard 
# Redundant because of points model?? FIX AFTER!!
class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False, unique=True)
    level = db.Column(db.Integer, default=1)
    current_lesson_id = db.Column(db.Integer, ForeignKey('lesson.id'), nullable=True)
    # add lesson progress or unit progress attribute?
    xp = db.Column(db.Integer, default=0)
    next_level_xp = db.Column(db.Integer, default=1000) # added this attribute in case we want to gradually increase xp needed to level up
    current_streak = db.Column(db.Integer, default=0) # can delete streak attribute from user
    longest_streak = db.Column(db.Integer, default=0)

    user = db.relationship('User', back_populates='progress', uselist=False)
    current_lesson = db.relationship('Lesson', backref='user_progress')


