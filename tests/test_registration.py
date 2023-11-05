import pytest
from app.src.app import app
from app.src.auth import register
from app.src.models import User, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

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
