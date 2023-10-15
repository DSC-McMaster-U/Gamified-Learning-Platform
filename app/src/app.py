from flask import Flask, render_template
from models import db
from auth import auth

app = Flask(__name__)
app.register_blueprint(auth)

# # Configure and initalize database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

# db.create_all()