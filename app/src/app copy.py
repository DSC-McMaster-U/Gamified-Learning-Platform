from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Incorporated within auth.py blueprint
@app.route('/login')
def login():
    return render_template('login.html')

