import pytest
from app.src.app import app
from app.src.auth import register
from app.src.models import User, db

from flask import Flask, request, redirect, url_for

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

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
