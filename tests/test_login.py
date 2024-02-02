import pytest
from app.src.app import db, create_app

@pytest.fixture(scope='session')
def app():
    # set up a test flask application with a test client
    # creates an instance of flask application, register 'auth' blueprint with the test flask application
    # run the flask app in testing mode and create a test client for the app
    app = create_app(test_config={'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    # app.register_blueprint(auth)   # this blueprint is already registered...

    # Set up: enter application context (necessary for database operations)
    with app.app_context():
        # create database tables
        db.create_all()
    
    yield app
    
    # Tear down: deletes all database tables created by the application during the test after testing is complete
    with app.app_context():
        db.session.remove()
        db.drop_all()
        
@pytest.fixture
def client(app):
    # app = create_app(test_config={'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    return app.test_client()  

def test_login_page(client):
    # test if login page is accessible. sends HTTP GET request to login route of app, check if HTTP status code is 200 (200 means ok)
    response = client.get('/login')
    assert response.status_code == 200

def test_login_valid_user(client):
    # login with valid user credentials
    # send a HTTP POST request to the /register route, inserting a test user with a set password into the database
    responseRegister = client.post('/register', data={
        'name': 'James Smith',
        'username': 'jsmith',
        'date_of_birth': '2023-10-01',
        'grade': 'FOURTH',
        'email': 'test@example.com',
        'confirm_email': 'test@example.com',
        'password': 'testPassword-123',
        'confirm_password': 'testPassword-123'
    }, follow_redirects=True)
    
    # should return a 200 OK status on successful registration
    assert responseRegister.status_code == 200

    # send HTTP POST request to the /login route with test user info, simulates the process of user submitting a login form
    responseLogin = client.post('/login', data={'email': 'test@example.com', 'password': 'testPassword-123'}) 
    # redirect on successful login, 302 = "found" redirection response
    assert responseLogin.status_code == 302

def test_login_invalid_user(client):
    # send HTTP POST request to "/register" in order to register a valid test user for the below tests
    responseRegister = client.post('/register', data={
        'name': 'John Doe',
        'username': 'jdoe',
        'date_of_birth': '2000-04-20',
        'grade': 'SOPHOMORE',
        'email': 'jdoe@example.com',
        'confirm_email': 'jdoe@example.com',
        'password': 'testPassword-123',
        'confirm_password': 'testPassword-123'
    }, follow_redirects=True)
    
    # should return a 200 OK status on successful registration
    assert responseRegister.status_code == 200

    # 1. test wrong email and password
    response = client.post('/login', data={'email': 'nonexistent@example.com', 'password': 'wrongpassword'})
    # re-render login page, 302 means there was a page redirect--in this case, from an unsuccessful login attempt
    assert response.status_code == 302
    assert response.location == '/login'
    # assert b'A user with this email does not exist!' in response.data 
    # ^ Note: This doesn't work, as what is returned is a temp "Redirecting..." page, not the login page with the error

    # 2. test wrong email
    response = client.post('/login', data={'email': 'nonexistent@example.com', 'password': 'testpassword'})
    assert response.status_code == 302
    assert response.location == '/login'

    # 3. test wrong password
    response = client.post('/login', data={'email': 'jdoe@example.com', 'password': 'wrongpassword'})
    assert response.status_code == 302
    assert response.location == '/login'

    # 4. test correct email but empty password field
    response = client.post('/login', data={'email': 'jdoe@example.com', 'password': ''})
    assert response.status_code == 302
    assert response.location == '/login'

    # 5. test empty email field, correct password
    response = client.post('/login', data={'email': '', 'password': 'testpassword'})
    assert response.status_code == 302
    assert response.location == '/login'

    # 6. both fields are empty
    response = client.post('/login', data={'email': '', 'password': ''})
    assert response.status_code == 302
    assert response.location == '/login'

    # 7. test user login locked account; make 3 more invalid login POST requests to trigger locked out flash message
    responses = [client.post('/login', data={'email': 'jdoe@example.com', 'password': 'wrong'}) for response in range(4)]
    
    # Get the response code and location of all three responses in sets (should be the same elements, so each set should have only one element inside it)
    resStatusCode = set(map(lambda res : res.status_code, responses)) # Value should be: {302}
    resLocation = set(map(lambda res : res.location, responses))      # Value should be: {'/login'}

    # Check if only one type of HTTP status code and only one type of page being redirected to ('/login')
    assert len(resStatusCode) == 1
    assert len(resLocation) == 1

    # Actually checking what the status code and page redirection is for all past 3 login requests
    assert list(resStatusCode)[0] == 302
    assert list(resLocation)[0] == '/login'

    # Send final HTTP POST request to trigger locked out error message
    responseLock = client.post('/login', data={'email': 'jdoe@example.com', 'password': 'wrong'})
    assert responseLock.status_code == 302
    assert responseLock.location == '/login'

    # 8. checking resulting flashed messages from page redirects
    with client.session_transaction() as session:
        flashed_messages = session['_flashes']
        print(flashed_messages)

        assert 'A user with this email does not exist!' in flashed_messages[0]
        assert 'A user with this email does not exist!' in flashed_messages[1]
        assert 'Incorrect password. Try again or click Forgot password to reset it.' in flashed_messages[2]
        assert 'Incorrect password. Try again or click Forgot password to reset it.' in flashed_messages[3]
        assert 'A user with this email does not exist!' in flashed_messages[4]
        assert 'A user with this email does not exist!' in flashed_messages[5]
        
        assert len(set(flashed_messages[6:10])) == 1   # Check that the first two HTTP requests of test 7. are normal invalid pass messages
        assert 'Incorrect password. Try again or click Forgot password to reset it.' in list(set(flashed_messages[6:10]))[0] 

        assert 'This account is locked. Please contact support to unlock your account and reset your password.' in flashed_messages[10]

def test_login_html_header(client):
    # Tests if HTML header element is present on the page
    response=client.get('/login')
    assert response.status_code == 200

    # Tests for presence of header
    assert b'<h1>Sign in to Your Account</h1>' in response.data

def test_login_html_form(client):
    # Tests if HTML input fields and form button elements are present on the page
    response=client.get('/login')
    assert response.status_code == 200

    # Tests for number of input fields
    assert b'name="email"' in response.data
    assert b'name="password"' in response.data
    assert b'type="submit"' in response.data
