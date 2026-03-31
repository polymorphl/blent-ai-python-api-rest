from src.models import User


# ---------------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_ok(self, client, app):
        response = client.post('/api/auth/register', json={
            "email": "test@test.com",
            "password": "password123",
            "name": "Test User"
        })
        assert response.status_code == 201

        with app.app_context():
            user = User.find_one("test@test.com")
            assert user is not None

    def test_duplicate(self, client, registered_user):
        response = client.post('/api/auth/register', json={
            "email": "test@test.com",
            "password": "password123",
            "name": "Test User"
        })
        assert response.status_code == 400

    def test_invalid_payload(self, client):
        response = client.post('/api/auth/register', json={
            "email": "test@test.com",
            "password": "password123",
        })
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_ok(self, client, registered_user):
        response = client.post('/api/auth/login', json={
            "email": "test@test.com",
            "password": "password123",
        })
        assert response.status_code == 200
        assert 'access_token' in response.get_json()

    def test_invalid_password(self, client, registered_user):
        response = client.post('/api/auth/login', json={
            "email": "test@test.com",
            "password": "another-password",
        })
        assert response.status_code == 401

    def test_invalid_payload(self, client, registered_user):
        response = client.post('/api/auth/login', json={
            "email": "test@test.com"
        })
        assert response.status_code == 400
