import pytest
from src import create_app
from src.config import TestConfig
from src.extensions import db


@pytest.fixture()
def app():
    app = create_app(TestConfig)

    # Create tables
    with app.app_context():
        db.create_all()

    yield app

    # Flush after each test
    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def registered_user(client):
    client.post('/api/auth/register', json={
        "email": "test@test.com",
        "password": "password123",
        "name": "Test User"
    })
