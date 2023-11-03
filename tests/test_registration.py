import pytest
from app.src.app import app
from app.src.auth import register
from app.src.models import User, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register(client):
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