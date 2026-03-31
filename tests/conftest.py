import pytest
from src import create_app
from src.config import TestConfig
from src.extensions import db
from src.models import User, Product, Role


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

# --- Access Tokens ---


@pytest.fixture()
def admin_token(client, app):
    with app.app_context():
        user = User(email="admin@test.com", nom="Admin", role=Role.ADMIN)
        user.set_password("admin1234")
        db.session.add(user)
        db.session.commit()
    response = client.post('/api/auth/login', json={
        "email": "admin@test.com",
        "password": "admin1234",
    })
    return response.get_json()["access_token"]


@pytest.fixture()
def client_token(client, app):
    with app.app_context():
        user = User(email="client@test.com", nom="Client", role=Role.CLIENT)
        user.set_password("client1234")
        db.session.add(user)
        db.session.commit()
    response = client.post('/api/auth/login', json={
        "email": "client@test.com",
        "password": "client1234",
    })
    return response.get_json()["access_token"]

# --- Products ---


@pytest.fixture()
def sample_product(app):
    with app.app_context():
        product = Product(
            nom="Clavier mécanique",
            description="Clavier RGB switches Cherry MX",
            categorie="Périphériques",
            prix=89.99,
            quantite_stock=15,
        )
        db.session.add(product)
        db.session.commit()
        return product.id
