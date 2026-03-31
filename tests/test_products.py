from conftest import auth_headers


# ---------------------------------------------------------------------------
# GET /api/produits
# ---------------------------------------------------------------------------

class TestListProducts:
    def test_empty(self, client):
        response = client.get('/api/produits')
        assert response.status_code == 200
        assert response.get_json()["products"] == []

    def test_with_product(self, client, sample_product):
        response = client.get('/api/produits')
        assert response.status_code == 200
        products = response.get_json()["products"]
        assert len(products) == 1
        assert products[0]["nom"] == "Clavier mécanique"

    def test_search_by_nom(self, client, sample_product):
        response = client.get('/api/produits?search=clavier')
        assert response.status_code == 200
        assert len(response.get_json()["products"]) == 1

    def test_search_by_categorie(self, client, sample_product):
        response = client.get('/api/produits?search=périphériques')
        assert response.status_code == 200
        assert len(response.get_json()["products"]) == 1

    def test_search_no_match(self, client, sample_product):
        response = client.get('/api/produits?search=zzz_introuvable')
        assert response.status_code == 200
        assert response.get_json()["products"] == []


# ---------------------------------------------------------------------------
# GET /api/produits/<id>
# ---------------------------------------------------------------------------

class TestGetProduct:
    def test_ok(self, client, sample_product):
        response = client.get(f'/api/produits/{sample_product}')
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == sample_product
        assert data["nom"] == "Clavier mécanique"
        assert "prix" in data
        assert "quantite_stock" in data
        assert "date_creation" in data

    def test_not_found(self, client):
        response = client.get('/api/produits/9999')
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/produits
# ---------------------------------------------------------------------------

class TestCreateProduct:
    def test_no_token(self, client):
        response = client.post('/api/produits', json={"nom": "Test"})
        assert response.status_code == 401

    def test_client_forbidden(self, client, client_token):
        response = client.post('/api/produits',
                               json={"nom": "Test"},
                               headers=auth_headers(client_token))
        assert response.status_code == 403

    def test_admin_ok(self, client, admin_token):
        response = client.post('/api/produits', json={
            "nom": "SSD 1To",
            "categorie": "Stockage",
            "prix": 129.99,
            "quantite_stock": 20,
        }, headers=auth_headers(admin_token))
        assert response.status_code == 201
        data = response.get_json()
        assert data["nom"] == "SSD 1To"
        assert data["quantite_stock"] == 20

    def test_default_stock(self, client, admin_token):
        response = client.post('/api/produits', json={
            "nom": "Souris gaming",
            "categorie": "Périphériques",
            "prix": 49.99,
        }, headers=auth_headers(admin_token))
        assert response.status_code == 201
        assert response.get_json()["quantite_stock"] == 0

    def test_missing_nom(self, client, admin_token):
        response = client.post('/api/produits', json={
            "categorie": "Stockage",
            "prix": 129.99,
        }, headers=auth_headers(admin_token))
        assert response.status_code == 400

    def test_missing_categorie(self, client, admin_token):
        response = client.post('/api/produits', json={
            "nom": "SSD",
            "prix": 129.99,
        }, headers=auth_headers(admin_token))
        assert response.status_code == 400

    def test_missing_prix(self, client, admin_token):
        response = client.post('/api/produits', json={
            "nom": "SSD",
            "categorie": "Stockage",
        }, headers=auth_headers(admin_token))
        assert response.status_code == 400

    def test_invalid_prix(self, client, admin_token):
        response = client.post('/api/produits', json={
            "nom": "SSD",
            "categorie": "Stockage",
            "prix": -10,
        }, headers=auth_headers(admin_token))
        assert response.status_code == 400

    def test_negative_stock(self, client, admin_token):
        response = client.post('/api/produits', json={
            "nom": "SSD",
            "categorie": "Stockage",
            "prix": 99.99,
            "quantite_stock": -5,
        }, headers=auth_headers(admin_token))
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# PUT /api/produits/<id>
# ---------------------------------------------------------------------------

class TestUpdateProduct:
    def test_no_token(self, client, sample_product):
        response = client.put(f'/api/produits/{sample_product}', json={"prix": 99})
        assert response.status_code == 401

    def test_client_forbidden(self, client, sample_product, client_token):
        response = client.put(f'/api/produits/{sample_product}',
                              json={"prix": 99},
                              headers=auth_headers(client_token))
        assert response.status_code == 403

    def test_admin_ok(self, client, sample_product, admin_token):
        response = client.put(f'/api/produits/{sample_product}',
                              json={"prix": 99.00, "quantite_stock": 5},
                              headers=auth_headers(admin_token))
        assert response.status_code == 200
        data = response.get_json()
        assert data["prix"] == 99.00
        assert data["quantite_stock"] == 5

    def test_not_found(self, client, admin_token):
        response = client.put('/api/produits/9999',
                              json={"prix": 99},
                              headers=auth_headers(admin_token))
        assert response.status_code == 404

    def test_invalid_prix(self, client, sample_product, admin_token):
        response = client.put(f'/api/produits/{sample_product}',
                              json={"prix": 0},
                              headers=auth_headers(admin_token))
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /api/produits/<id>
# ---------------------------------------------------------------------------

class TestDeleteProduct:
    def test_no_token(self, client, sample_product):
        response = client.delete(f'/api/produits/{sample_product}')
        assert response.status_code == 401

    def test_client_forbidden(self, client, sample_product, client_token):
        response = client.delete(f'/api/produits/{sample_product}',
                                 headers=auth_headers(client_token))
        assert response.status_code == 403

    def test_admin_ok(self, client, sample_product, admin_token):
        response = client.delete(f'/api/produits/{sample_product}',
                                 headers=auth_headers(admin_token))
        assert response.status_code == 200
        assert "supprimé" in response.get_json()["message"]

    def test_not_found(self, client, admin_token):
        response = client.delete('/api/produits/9999',
                                 headers=auth_headers(admin_token))
        assert response.status_code == 404

    def test_no_longer_accessible(self, client, sample_product, admin_token):
        client.delete(f'/api/produits/{sample_product}',
                      headers=auth_headers(admin_token))
        response = client.get(f'/api/produits/{sample_product}')
        assert response.status_code == 404
