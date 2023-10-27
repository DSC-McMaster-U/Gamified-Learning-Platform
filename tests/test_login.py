import unittest 
from flask import Flask
from app.src.app import db, create_app
from app.src.auth import auth
from app.src.models import User

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        # set up a test flask application with a test client
        self.app = Flask(__name__)
        self.app.register_blueprint(auth)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # cleans up the database
        with self.app.app_context():
            db.drop_all()

    def TestLoginPage(self):
        # test if login page is accessible
        response=self.client.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def TestLoginValidUser(self):
        # login with valid user credentials
        with self.app.app_context():
            test_user = User(email='test@example.com')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()

        response = self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})
        # redirect on successful login
        self.assertEqual(response.status_code, 302)

    def TestLoginInavlidUser(self):
        # login with invalid credentials
        response = self.client.post('/login', data={'email': 'nonexistent@example.com', 'password': 'wrongpassword'})
        # re-render login page
        self.assertEqual(response.status_code, 200) 

if __name__ == '__main__':
    unittest.main()