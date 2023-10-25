from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
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
    hashed_password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer, CheckConstraint('age >= 0 AND age <= 100', name='check_age_range'))
    grade = db.Column(SQLAlchemyEnum(GradeEnum), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.now(timezone(timedelta(hours=-5))))
    favorite_subject = db.Column(db.String(50))
    failed_signin_attempts = db.Integer(db.Integer, default=0)
    
    # Set user password
    def set_password(self, password):
        self.hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Check if entered password is correct
    def check_password(self, password):
        return bcrypt.check_password_hash(self.hashed_password, password)