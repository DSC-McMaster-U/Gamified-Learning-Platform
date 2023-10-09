from flask import Flask, render_template
from models import db

app = Flask(__name__)

# Configure and initalize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

db.create_all()