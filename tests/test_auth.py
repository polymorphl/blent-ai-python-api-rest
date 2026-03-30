from src.models import User


def test_register(client, app):
    response = client.post('/api/auth/register', json={
        "email": "test@test.com",
        "password": "password123",
        "name": "Test User"
    })
    assert response.status_code == 201

    with app.app_context():
        user = User.find_one("test@test.com")
        assert user is not None


def test_register_duplicate(client, registered_user):
    response = client.post('/api/auth/register', json={
        "email": "test@test.com",
        "password": "password123",
        "name": "Test User"
    })
    assert response.status_code == 400


def test_register_invalid_payload(client):
    response = client.post('/api/auth/register', json={
        "email": "test@test.com",
        "password": "password123",
    })

    assert response.status_code == 400


def test_login(client, registered_user):
    response = client.post('/api/auth/login', json={
        "email": "test@test.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert 'access_token' in response.get_json()


def test_login_invalid_password(client, registered_user):
    response = client.post('/api/auth/login', json={
        "email": "test@test.com",
        "password": "another-password",
    })
    assert response.status_code == 400


def test_login_invalid_payload(client, registered_user):
    response = client.post('/api/auth/login', json={
        "email": "test@test.com"
    })
    assert response.status_code == 400
