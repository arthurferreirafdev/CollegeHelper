import os
import pytest

os.environ['DATABASE_PATH'] = ':memory:'
os.environ['JWT_SECRET_KEY'] = 'test-secret'
os.environ['SECRET_KEY'] = 'test-secret'

from backend.app import create_app
from backend.repository.database import _memory_db


@pytest.fixture(autouse=True)
def reset_memory_db():
    """Reset the shared in-memory database between tests."""
    import backend.repository.database as db_module
    db_module._memory_db = None
    yield
    db_module._memory_db = None


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE_PATH'] = ':memory:'
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_token(client):
    client.post('/api/auth/register', json={
        'email': 'test@school.edu',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User',
        'grade_level': 11
    })
    resp = client.post('/api/auth/login', json={
        'email': 'test@school.edu',
        'password': 'password123'
    })
    return resp.get_json()['token']
