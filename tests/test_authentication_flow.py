import pytest
import tempfile
import os
from flask import get_flashed_messages
from app.src.app import create_app, db
from app.src.auth import login_post, register
from app.src.models import User, GradeEnum

@pytest.fixture
def client_tempdb():
    # create a temporary database for tests to avoid creating a database that will remain in the directory
    db_fd, db_fname = tempfile.mkstemp()
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_fname,
        'TESTING': True,
        'SECRET_KEY': 'your_secret_key',
        'WTF_CSRF_ENABLED': False,
    })

    with app.app_context():
        db.create_all()
    
        with app.test_client() as client:
            yield client, db # client must be created under the app context to ensure that the client can interact with the temporary database when making requests

        # this will execute after the tests are completed to delete the temporary database
        db.session.remove()
        db.session.close()
        db.drop_all()    

        # ISSUE: pytest seems to throw an exception here on Windows, due to how the OS handles temp files; in the future, try to look for workarounds regarding this problem.
        os.close(db_fd)
        os.unlink(db_fname)

def test_workflow(client_tempdb):
    client, db_handle = client_tempdb # Get the client and temporary database created in the fixture

    response = client.post('/register', data={'email': 'johndoe@gmail.com', 'confirm_email': 'johndoe@gmail.com', 'username': 'johndoe', 'password': 'John@123',
                                              'confirm_password': 'John@123', 'name': 'John Doe', 'grade': 'FOURTH', 'date_of_birth': '2000-01-01',}, follow_redirects=True)
    
    # assertion to check that the registration post request is successful (unsuccesful registration may still return 200 status code, however it will not return correct flash message)
    assert response.status_code == 200
    with client.session_transaction() as session:
        flashed_messages = get_flashed_messages()
        assert 'Registration Successful!' in flashed_messages

    # ensure that the user is successfully stored in the database
    user = User.query.filter_by(username='johndoe').first()
    assert user.email == 'johndoe@gmail.com'
    assert user.name == 'John Doe'
    assert user.check_password('John@123')

    response = client.post('/login', data={'email': 'johndoe@gmail.com', 'password': 'John@123'}, follow_redirects=True)

    # assertion to check that the login post request is successful given the user that was stored in the database
    assert response.status_code == 200
    with client.session_transaction() as session:
        flashed_messages = get_flashed_messages()
        assert 'Successfully logged in! Redirecting to dashboard...' in flashed_messages


# CREATE FUTURE TESTS TO CHECK FOR INCORRECT LOGIN GIVEN USER? (locked account and incorrect login)
# May need to set up new application contexts if we decide to create multiple test functions, to check the database (this way we can check the database to ensure that it contains the expected values)




