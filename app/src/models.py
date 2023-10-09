from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    hashed_password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.now(timezone(timedelta(hours=-5))))
    favorite_subject = db.Column(db.String(50))
    
    # Set user password
    def set_password(self, password):
        self.hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Check if entered password is correct
    def check_password(self, password):
        return bcrypt.check_password_hash(self.hashed_password, password)