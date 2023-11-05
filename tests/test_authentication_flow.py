import pytest
import tempfile
import os
from app.src.app import app, db
from app.src.auth import login_post, register
from app.src.models import User

@pytest.fixture
def client_tempdb():
    # create a temporary database for tests to avoid creating a database that will remain in the directory
    db_fd, db_fname = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_fname 
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF Protection so we do not have to retrieve CSRF token when creating user

    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client, db # client must be created under the app context to ensure that the client can interact with the temporary database when making requests

        # this will execute after the tests are completed to delete the temporary database
        db.session.remove()
        os.close(db_fd)
        os.unlink(db_fname)

def test_workflow(client_tempdb):
    client, db_handle = client_tempdb # Get the client and temporary database created in the fixture

    response = client.post('/register', data={'email': 'johndoe@gmail.com', 'username': 'johndoe', 'password': 'john123',
                                              'confirm_password': 'john123', 'name': 'John Doe', 'grade': ''}, follow_redirects=True)
    
    # assertion to check that the registration post request is successful (unsuccesful registration may still return 200 status code, however it will not return correct flash message)
    assert response.status_code == 200
    assert b'Registration Successful!' in response.data

    # ensure that the user is successfully stored in the database
    user = User.query.filter_by(username='johndoe').first()
    assert user.email == 'johndoe@gmail.com'
    assert user.name == 'John Doe'
    assert user.check_password('john123')

    response = client.post('/login', data={'email': 'johndoe@gmail.com', 'password': 'john123'}, follow_redirects=True)

    # assertion to check that the login post request is successful given the user that was stored in the database
    assert response.status.code == 200
    assert b'Successfully logged in! Redirecting to dashboard...' in response.data


# CREATE FUTURE TESTS TO CHECK FOR INCORRECT LOGIN GIVEN USER? (locked account and incorrect login)
# May need to set up new application contexts if we decide to create multiple test functions, to check the database (this way we can check the database to ensure that it contains the expected values)




