import pytest
from app.src.app import create_app, db
from app.src.auth import register
from app.src.models import User
from flask import get_flashed_messages, session

@pytest.fixture
def app():
    app = create_app(test_config={'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()
        
@pytest.fixture
def client(app):
    return app.test_client()


def test_register_valid(client):
    with client:   # Changed flash messages with block layout, as this test was raising a keyError with session['_flashes'] before
        # valid inputs, follow redirect should be OK (200)
        response1 = client.post('/register', data={
            'name': 'James Smith',
            'username': 'jsmith',
            'date_of_birth': '2023-10-01',
            'grade': 'FOURTH',
            'email': 'jsmith99@gmail.com',
            'confirm_email': 'jsmith99@gmail.com',
            'password': 'jSmith123-',
            'confirm_password': 'jSmith123-'
        }, follow_redirects=True)
        assert response1.status_code == 200
        
        response2 = client.post('/register', data={
            'name': 'John Doe',
            'username': 'johndoe00',
            'date_of_birth': '2006-04-25',
            'grade': 'FOURTH',
            'email': 'johndoe@gmail.com',
            'confirm_email': 'johndoe@gmail.com',
            'password': 'jDoe2000!',
            'confirm_password': 'jDoe2000!'
        }, follow_redirects=True)
        assert response2.status_code == 200

        # should flash "Registration Successful!"
        flashed_messages = session['_flashes']
        assert 'Registration Successful!' in flashed_messages[0]
        # assert 'Registration Successful!' in flashed_messages[1] 
    
def test_register_invalid(client):
    # invalid inputs, not follow redirect should be Found (302)
    # the new URL should be /register
    response1 = client.post('/register', data={
        'name': 'James Smith',
        'username': 'jsmith',
        'date_of_birth': '2023-10-01',
        'grade': 'SOPHOMORE',
        'email': 'jsmith99@gmail.com',
        'confirm_email': 'jsmith99@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'jSmith123-'
    })
    assert response1.status_code == 302
    assert response1.location == '/login'
    
    # duplicate email
    response2 = client.post('/register', data={
        'name': 'James Smith',
        'username': 'jsmith123',
        'date_of_birth': '2023-01-10',
        'grade': 'FOURTH',
        'email': 'jsmith99@gmail.com',
        'confirm_email': 'jsmith99@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'jSmith123-'
    })
    assert response2.status_code == 302
    assert response2.location == '/register'
    
    # duplicate username
    response3 = client.post('/register', data={
        'name': 'James Smith',
        'username': 'jsmith',
        'date_of_birth': '2006-04-25',
        'grade': 'FIFTH',
        'email': 'jsmith2000@gmail.com',
        'confirm_email': 'jsmith2000@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'jSmith123-'
    })
    assert response3.status_code == 302
    assert response3.location == '/register'
    
    # no password
    response4 = client.post('/register', data={
        'name': 'James Smith',
        'username': 'username',
        'date_of_birth': '2006-04-25',
        'grade': 'NA',
        'email': 'email@gmail.com',
        'confirm_email': 'email@gmail.com',
        'password': '',
        'confirm_password': 'jSmith123-'
    })
    assert response4.status_code == 302
    assert response4.location == '/register'
    
    # different passwords
    response5 = client.post('/register', data={
        'name': 'James Smith',
        'username': 'username',
        'date_of_birth': '2006-04-25',
        'grade': 'FIRST',
        'email': 'email@gmail.com',
        'confirm_email': 'email@gmail.com',        
        'password': 'johnSmith123-',
        'confirm_password': 'jSmith123-'
    })
    assert response5.status_code == 302
    assert response5.location == '/register'
    
    # different emails
    response6 = client.post('/register', data={
        'name': 'James Smith',
        'username': 'username',
        'date_of_birth': '2006-04-25',
        'grade': 'FIRST',
        'email': 'email@gmail.com',
        'confirm_email': 'anotherEmail@gmail.com',        
        'password': 'johnSmith123-',
        'confirm_password': 'johnSmith123-'
    })
    assert response6.status_code == 302
    assert response6.location == '/register'

    # no name
    response7 = client.post('/register', data={
        'name': '',
        'username': 'username',
        'date_of_birth': '2006-04-25',
        'grade': 'THIRD',
        'email': 'email@gmail.com',
        'confirm_email': 'email@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'jSmith123-'
    })
    assert response7.status_code == 302
    assert response7.location == '/register'
    
    # weak password
    response8 = client.post('/register', data={
        'name': 'name',
        'username': 'username',
        'date_of_birth': '2006-04-25',
        'grade': 'THIRD',
        'email': 'email@gmail.com',
        'confirm_email': 'email@gmail.com',
        'password': 'jSmith-',
        'confirm_password': 'jSmith-'
    })
    assert response8.status_code == 302
    assert response8.location == '/register'
    
    # invalid methods, should be Method Not Allowed (405)
    response9 = client.delete('/register', data={
        'name': 'James Smith',
        'username': 'jsmith',
        'date_of_birth': '2023-10-01',
        'grade': 'FOURTH',
        'email': 'jsmith99@gmail.com',
        'confirm_email': 'jsmith99@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'jSmith123-'
    })
    assert response9.status_code == 405
    
    response10 = client.put('/register', data={
        'name': 'James Smith',
        'username': 'jsmith',
        'date_of_birth': '2023-10-01',
        'grade': 'FOURTH',
        'email': 'jsmith99@gmail.com',
        'confirm_email': 'jsmith99@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'jSmith123-'
    })
    assert response10.status_code == 405
    
    # validating flash messages
    with client.session_transaction() as session:
        flashed_messages = session['_flashes']
        print(flashed_messages)
        assert 'Registration Successful!' in flashed_messages[0]
        assert 'This email already exists.' in flashed_messages[1]
        assert 'This username already exists.' in flashed_messages[2]
        assert 'You must provide a password.' in flashed_messages[3]
        assert 'The passwords do not match!' in flashed_messages[4]
        assert 'The emails do not match!' in flashed_messages[5]
        assert 'You must provide your name.' in flashed_messages[6]
        assert 'Password is not strong enough. Here are some suggestions: Length(8), Numbers(1)' in flashed_messages[7]


# Check if the registration page is accessible and header is present
def test_header(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b"<h1>Registration</h1>" in response.data

# Check for the presence of input fields within the form
def test_formFields(client):
    response = client.get('/register')
    assert response.status_code == 200  
    assert b'name="name"' in response.data
    assert b'name="username"' in response.data
    assert b'name="date_of_birth"' in response.data
    assert b'name="grade"' in response.data
    assert b'name="email"' in response.data
    assert b'name="confirm_email"' in response.data
    assert b'name="password"' in response.data
    assert b'name="confirm_password"' in response.data

# Check if the submit button is present
def test_signup(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'type="submit"' in response.data

# Check if other important links are there
def test_links(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'href="/login.html"' in response.data
    assert b'href="/user_profile.html"' in response.data