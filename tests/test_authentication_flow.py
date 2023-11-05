import pytest
import tempfile
import os
from app.src.app import app, db

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



