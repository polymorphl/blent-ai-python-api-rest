import pytest
from src import create_app
from src.config import TestConfig
from src.extensions import db
from src.models import User, Product, Order, OrderLine, Role


@pytest.fixture()
def app():
    """Crée l'application Flask avec la configuration de test et initialise la base de données."""
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
    """Retourne le client de test Flask."""
    return app.test_client()


@pytest.fixture()
def registered_user(client):
    """Enregistre un utilisateur de base via l'endpoint d'inscription."""
    client.post('/api/auth/register', json={
        "email": "test@test.com",
        "password": "password123",
        "name": "Test User"
    })

# --- Helpers ---

def auth_headers(token):
    """Retourne les headers d'authentification Bearer pour un token donné."""
    return {"Authorization": f"Bearer {token}"}

# --- Access Tokens ---


@pytest.fixture()
def admin_token(client, app):
    """Crée un utilisateur admin et retourne son access token JWT."""
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
    """Crée un utilisateur client et retourne son access token JWT."""
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
    """Crée un produit en base et retourne son id."""
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


@pytest.fixture()
def sample_product_with_stock(app):
    """Crée un produit avec du stock disponible en base et retourne son id."""
    with app.app_context():
        product = Product(
            nom="Souris sans fil",
            categorie="Périphériques",
            prix=49.99,
            quantite_stock=10,
        )
        db.session.add(product)
        db.session.commit()
        return product.id

# --- Orders ---


@pytest.fixture()
def client_user_id(app, client_token):
    """Retourne l'id de l'utilisateur client."""
    with app.app_context():
        user = User.find_one("client@test.com")
        return user.id


@pytest.fixture()
def sample_order(app, client_user_id, sample_product_with_stock):
    """Crée une commande avec une ligne pour l'utilisateur client."""
    with app.app_context():
        product = db.session.get(Product, sample_product_with_stock)
        order = Order(
            utilisateur_id=client_user_id,
            adresse_livraison="10 rue de la Paix, 75001 Paris",
        )
        db.session.add(order)
        db.session.flush()
        line = OrderLine(
            commande_id=order.id,
            produit_id=product.id,
            quantite=2,
            prix_unitaire=product.prix,
        )
        db.session.add(line)
        product.quantite_stock -= 2
        db.session.commit()
        return order.id
