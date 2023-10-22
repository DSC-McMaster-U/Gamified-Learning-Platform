from flask import Flask, render_template, redirect
# from auth import auth

app = Flask(__name__)
# app.register_blueprint(auth)

@app.route('/')
def index():
    return render_template('index.html')

# Incorporated within auth.py blueprint
@app.route('/login.html')
def redirectLogin():
    return redirect('/login', code = 302)   # Probably should change 302 redirect code later

@app.route('/login')
def login():
    # Temp logged in value for now
    loggedIn = False
    return render_template('login.html', logged_in = loggedIn)

