import unittest 
from flask import Flask
from app.src.app import db, create_app
from app.src.auth import auth
from app.src.models import User

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        # set up a test flask application with a test client
        # creates an instance of flask application, register 'auth' blueprint with the test flask application
        # run the flask app in testing mode and create a test client for the app
        self.app = Flask(__name__) 
        self.app.register_blueprint(auth) 
        self.app.config['TESTING'] = True 
        self.client = self.app.test_client() 

        # enter application context (necessary for database operations)
        with self.app.app_context():
            # create database tables
            db.create_all()

    def tearDown(self):
        # deletes all database tables created by the application during the test after testing is complete
        with self.app.app_context():
            db.drop_all()

    def TestLoginPage(self):
        # test if login page is accessible. sends HTTP GET request to login route of app, check if HTTP status code is 200 (200 means ok)
        response=self.client.get('/login')
        self.assertEqual(response.status_code, 200) 
    
    def TestLoginValidUser(self):
        # login with valid user credentials
        # enter application context using context maanger; create test user and set password; add test user to databse, and commit changes to database,
        # inserting the user into the database
        with self.app.app_context(): 
            test_user = User(email='test@example.com')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit() 

        # send HTTP POST request to the /login route with test user info, simulates the process of user submitting a login form
        response = self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'}) 
        # redirect on successful login, 302 = "found" redirection response
        self.assertEqual(response.status_code, 302)

    def TestLoginInavlidUser(self):

        with self.app.app_context(): 
            test_user = User(email='test@example.com')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit() 

        # test wrong email and password
        response = self.client.post('/login', data={'email': 'nonexistent@example.com', 'password': 'wrongpassword'})
        # re-render login page, 200 means 'ok' as well as unsuccessful login attempt
        self.assertEqual(response.status_code, 200) 
        self.assertIn(b'Invalid email or password', response.data)

        # test wrong email
        response = self.client.post('/login', data={'email': 'nonexistent@example.com', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)

        # test wrong password
        response = self.client.post('/login', data={'email': 'test@example.com', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)

        # test correct email but empty password field
        response = self.client.post('/login', data={'email': 'test@example.com', 'password': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password is required', response.data)

        # test empty email field, correct password
        response = self.client.post('/login', data={'email': '', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email is required', response.data)

        # both fields are empty
        response = self.client.post('/login', data={'email': '', 'password': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email is required', response.data)
        self.assertIn(b'Password is required', response.data)

if __name__ == '__main__':
    unittest.main()