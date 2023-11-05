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

        db.session.remove()
        os.close(db_fd)
        os.unlink(db_fname)

def test_workflow(client_tempdb):
    client, db_handle = client_tempdb # Get the client and temporary database created in the fixture

    response = client.post('/register', data={'email': 'johndoe@gmail.com', 'username': 'johndoe', 'password': 'john123',
                                              'confirm_password': 'john123', 'name': 'John Doe', 'grade': ''}, follow_redirects=True)
    
    # assertion to check that the registration post request is successful
    assert response.status_code == 200



