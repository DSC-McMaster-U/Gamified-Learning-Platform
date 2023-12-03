import pytest
from app.src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_hello_world(client):
    response = client.get('/')
    assert response.status_code == 200
    
