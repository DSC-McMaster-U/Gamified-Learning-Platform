import pytest
from app.src.app import create_app, db
from app.src.auth import register
from app.src.models import User

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


def test_register(client):
    # valid inputs, follow redirect should be OK (200)
    response1 = client.post('/register', data={
        'name': 'James Smith',
        'username': 'jsmith',
        'date_of_birth': '2023-10-01',
        'grade': '',
        'email': 'jsmith99@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'jSmith123-'
    }, follow_redirects=True)
    assert response1.status_code == 200
    
    # valid or invalid inputs, not follow redirect should be Found (302)
    # the new URL should be /register
    response2 = client.post('/register', data={
        'name': 'James Smith',
        'username': 'jsmith',
        'date_of_birth': '2023-10-01',
        'grade': '',
        'email': 'jsmith99@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'jSmith123-'
    })
    assert response2.status_code == 302
    assert response2.location == '/register'
    
    response3 = client.post('/register', data={
        'name': 'James Smith',
        'username': 'jsmith',
        'date_of_birth': '2023-10-01',
        'grade': '',
        'email': 'jsmith99@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'differentPassword-'
    })
    assert response3.status_code == 302
    assert response3.location == '/register'
    
    # invalid methods, should be Method Not Allowed (405)
    response4 = client.delete('/register', data={
        'name': 'James Smith',
        'username': 'jsmith',
        'date_of_birth': '2023-10-01',
        'grade': '',
        'email': 'jsmith99@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'jSmith123-'
    })
    assert response4.status_code == 405
    
    response5 = client.put('/register', data={
        'name': 'James Smith',
        'username': 'jsmith',
        'date_of_birth': '2023-10-01',
        'grade': '',
        'email': 'jsmith99@gmail.com',
        'password': 'jSmith123-',
        'confirm_password': 'jSmith123-'
    })
    assert response5.status_code == 405

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