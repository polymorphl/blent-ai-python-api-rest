from conftest import auth_headers


# ---------------------------------------------------------------------------
# GET /api/commandes
# ---------------------------------------------------------------------------

class TestListOrders:
    def test_unauthorized(self, client):
        r = client.get('/api/commandes')
        assert r.status_code == 401

    def test_client_only_dedicated_orders(
        self, client, client_token, sample_order
    ):
        r = client.get(
            '/api/commandes',
            headers=auth_headers(client_token)
        )
        assert r.status_code == 200
        data = r.get_json()
        assert "orders" in data
        assert len(data["orders"]) == 1

    def test_admin_see_all(
        self, client, admin_token, sample_order
    ):
        r = client.get(
            '/api/commandes',
            headers=auth_headers(admin_token)
        )
        assert r.status_code == 200
        assert len(r.get_json()["orders"]) >= 1

    def test_client_no_orders(
        self, client, client_token
    ):
        r = client.get(
            '/api/commandes',
            headers=auth_headers(client_token)
        )
        assert r.status_code == 200
        assert r.get_json()["orders"] == []


# ---------------------------------------------------------------------------
# GET /api/commandes/<id>
# ---------------------------------------------------------------------------

class TestGetOrder:
    def test_not_found(self, client, client_token):
        r = client.get(
            '/api/commandes/9999',
            headers=auth_headers(client_token)
        )
        assert r.status_code == 404

    def test_client_access_forbidden_order(
        self, client, admin_token, client_token, sample_order
    ):
        # Créer une seconde commande appartenant à l'admin via l'API
        # Ici sample_order appartient au client,
        # on vérifie qu'un autre client n'y accède pas.
        # On crée un second client via register puis on tente d'y accéder.
        client.post('/api/auth/register', json={
            "email": "other@test.com",
            "password": "pass1234",
            "name": "Other"
        })
        login_r = client.post('/api/auth/login', json={
            "email": "other@test.com",
            "password": "pass1234"
        })
        other_token = login_r.get_json()["access_token"]

        r = client.get(
            f'/api/commandes/{sample_order}',
            headers=auth_headers(other_token)
        )
        assert r.status_code == 403

    def test_client_access_owned_order(
        self, client, client_token, sample_order
    ):
        r = client.get(
            f'/api/commandes/{sample_order}',
            headers=auth_headers(client_token)
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data["id"] == sample_order

    def test_admin_acces_any_order(
        self, client, admin_token, sample_order
    ):
        r = client.get(
            f'/api/commandes/{sample_order}',
            headers=auth_headers(admin_token)
        )
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/commandes
# ---------------------------------------------------------------------------

class TestCreateOrder:
    def test_missing_token(self, client):
        r = client.post('/api/commandes', json={})
        assert r.status_code == 401

    def test_empty_payload(self, client, client_token):
        r = client.post(
            '/api/commandes',
            json={},
            headers=auth_headers(client_token)
        )
        assert r.status_code == 400

    def test_missing_address(
        self, client, client_token, sample_product_with_stock
    ):
        r = client.post(
            '/api/commandes',
            json={"lines": [
                {"produit_id": sample_product_with_stock, "quantite": 1}]},
            headers=auth_headers(client_token)
        )
        assert r.status_code == 400

    def test_empty_lines(self, client, client_token):
        r = client.post(
            '/api/commandes',
            json={"adresse_livraison": "1 rue Test", "lines": []},
            headers=auth_headers(client_token)
        )
        assert r.status_code == 400

    def test_missing_product(self, client, client_token):
        r = client.post(
            '/api/commandes',
            json={
                "adresse_livraison": "1 rue Test",
                "lines": [{"produit_id": 9999, "quantite": 1}]
            },
            headers=auth_headers(client_token)
        )
        assert r.status_code == 404

    def test_missing_stock(
        self, client, client_token, sample_product_with_stock
    ):
        r = client.post(
            '/api/commandes',
            json={
                "adresse_livraison": "1 rue Test",
                "lines": [{
                    "produit_id": sample_product_with_stock,
                    "quantite": 999
                }]
            },
            headers=auth_headers(client_token)
        )
        assert r.status_code == 400

    def test_order_ok_and_decrease_stock(
        self, client, client_token, sample_product_with_stock, app
    ):
        r = client.post(
            '/api/commandes',
            json={
                "adresse_livraison": "10 rue de la Paix, 75001 Paris",
                "lines": [{
                    "produit_id": sample_product_with_stock,
                    "quantite": 3
                }]
            },
            headers=auth_headers(client_token)
        )
        assert r.status_code == 201
        data = r.get_json()
        assert data["adresse_livraison"] == "10 rue de la Paix, 75001 Paris"
        assert data["statut"] == "en_attente"
        assert data["lines_len"] == 1

        # Vérifier que le stock a été décrémenté
        from src.models import Product
        from src.extensions import db
        with app.app_context():
            product = db.session.get(Product, sample_product_with_stock)
            assert product.quantite_stock == 7  # 10 - 3


# ---------------------------------------------------------------------------
# PATCH /api/commandes/<id>
# ---------------------------------------------------------------------------

class TestUpdateOrderStatus:
    def test_client_forbidden(
        self, client, client_token, sample_order
    ):
        r = client.patch(
            f'/api/commandes/{sample_order}',
            json={"statut": "validée"},
            headers=auth_headers(client_token)
        )
        assert r.status_code == 403

    def test_missing_order(self, client, admin_token):
        r = client.patch(
            '/api/commandes/9999',
            json={"statut": "validée"},
            headers=auth_headers(admin_token)
        )
        assert r.status_code == 404

    def test_invalid_status(
        self, client, admin_token, sample_order
    ):
        r = client.patch(
            f'/api/commandes/{sample_order}',
            json={"statut": "inconnu"},
            headers=auth_headers(admin_token)
        )
        assert r.status_code == 400

    def test_patch_order_ok(
        self, client, admin_token, sample_order
    ):
        r = client.patch(
            f'/api/commandes/{sample_order}',
            json={"statut": "validée"},
            headers=auth_headers(admin_token)
        )
        assert r.status_code == 200
        assert r.get_json()["statut"] == "validée"


# ---------------------------------------------------------------------------
# GET /api/commandes/<id>/lignes
# ---------------------------------------------------------------------------

class TestGetOrderLines:
    def test_missing_order(self, client, client_token):
        r = client.get(
            '/api/commandes/9999/lignes',
            headers=auth_headers(client_token)
        )
        assert r.status_code == 404

    def test_forbidden_order_lines(
        self, client, sample_order
    ):
        client.post('/api/auth/register', json={
            "email": "other2@test.com",
            "password": "pass1234",
            "name": "Other2"
        })
        login_r = client.post('/api/auth/login', json={
            "email": "other2@test.com",
            "password": "pass1234"
        })
        other_token = login_r.get_json()["access_token"]

        r = client.get(
            f'/api/commandes/{sample_order}/lignes',
            headers=auth_headers(other_token)
        )
        assert r.status_code == 403

    def test_access_order_lines(
        self, client, client_token, sample_order
    ):
        r = client.get(
            f'/api/commandes/{sample_order}/lignes',
            headers=auth_headers(client_token)
        )
        assert r.status_code == 200
        data = r.get_json()
        assert "lines" in data
        assert len(data["lines"]) == 1
        ligne = data["lines"][0]
        assert "produit_id" in ligne
        assert "quantite" in ligne
        assert "prix_unitaire" in ligne
