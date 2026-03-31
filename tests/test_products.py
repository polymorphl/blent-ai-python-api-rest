def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# --- GET /api/produits ---

def test_list_products_empty(client):
    response = client.get('/api/produits')
    assert response.status_code == 200
    assert response.get_json()["products"] == []


def test_list_products(client, sample_product):
    response = client.get('/api/produits')
    assert response.status_code == 200
    products = response.get_json()["products"]
    assert len(products) == 1
    assert products[0]["nom"] == "Clavier mécanique"


def test_list_products_search_by_nom(client, sample_product):
    response = client.get('/api/produits?search=clavier')
    assert response.status_code == 200
    assert len(response.get_json()["products"]) == 1


def test_list_products_search_by_categorie(client, sample_product):
    response = client.get('/api/produits?search=périphériques')
    assert response.status_code == 200
    assert len(response.get_json()["products"]) == 1


def test_list_products_search_no_match(client, sample_product):
    response = client.get('/api/produits?search=zzz_introuvable')
    assert response.status_code == 200
    assert response.get_json()["products"] == []


# --- GET /api/produits/<id> ---

def test_get_product(client, sample_product):
    response = client.get(f'/api/produits/{sample_product}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == sample_product
    assert data["nom"] == "Clavier mécanique"
    assert "prix" in data
    assert "quantite_stock" in data
    assert "date_creation" in data


def test_get_product_not_found(client):
    response = client.get('/api/produits/9999')
    assert response.status_code == 404


# --- POST /api/produits ---

def test_create_product_no_token(client):
    response = client.post('/api/produits', json={"nom": "Test"})
    assert response.status_code == 401


def test_create_product_client_forbidden(client, client_token):
    response = client.post('/api/produits',
                           json={"nom": "Test"},
                           headers=auth_headers(client_token))
    assert response.status_code == 403


def test_create_product_admin(client, admin_token):
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


def test_create_product_default_stock(client, admin_token):
    response = client.post('/api/produits', json={
        "nom": "Souris gaming",
        "categorie": "Périphériques",
        "prix": 49.99,
    }, headers=auth_headers(admin_token))
    assert response.status_code == 201
    assert response.get_json()["quantite_stock"] == 0


def test_create_product_missing_nom(client, admin_token):
    response = client.post('/api/produits', json={
        "categorie": "Stockage",
        "prix": 129.99,
    }, headers=auth_headers(admin_token))
    assert response.status_code == 400


def test_create_product_missing_categorie(client, admin_token):
    response = client.post('/api/produits', json={
        "nom": "SSD",
        "prix": 129.99,
    }, headers=auth_headers(admin_token))
    assert response.status_code == 400


def test_create_product_missing_prix(client, admin_token):
    response = client.post('/api/produits', json={
        "nom": "SSD",
        "categorie": "Stockage",
    }, headers=auth_headers(admin_token))
    assert response.status_code == 400


def test_create_product_invalid_prix(client, admin_token):
    response = client.post('/api/produits', json={
        "nom": "SSD",
        "categorie": "Stockage",
        "prix": -10,
    }, headers=auth_headers(admin_token))
    assert response.status_code == 400


def test_create_product_negative_stock(client, admin_token):
    response = client.post('/api/produits', json={
        "nom": "SSD",
        "categorie": "Stockage",
        "prix": 99.99,
        "quantite_stock": -5,
    }, headers=auth_headers(admin_token))
    assert response.status_code == 400


# --- PUT /api/produits/<id> ---

def test_update_product_no_token(client, sample_product):
    response = client.put(f'/api/produits/{sample_product}', json={"prix": 99})
    assert response.status_code == 401


def test_update_product_client_forbidden(client, sample_product, client_token):
    response = client.put(f'/api/produits/{sample_product}',
                          json={"prix": 99},
                          headers=auth_headers(client_token))
    assert response.status_code == 403


def test_update_product_admin(client, sample_product, admin_token):
    response = client.put(f'/api/produits/{sample_product}',
                          json={"prix": 99.00, "quantite_stock": 5},
                          headers=auth_headers(admin_token))
    assert response.status_code == 200
    data = response.get_json()
    assert data["prix"] == 99.00
    assert data["quantite_stock"] == 5


def test_update_product_not_found(client, admin_token):
    response = client.put('/api/produits/9999',
                          json={"prix": 99},
                          headers=auth_headers(admin_token))
    assert response.status_code == 404


def test_update_product_invalid_prix(client, sample_product, admin_token):
    response = client.put(f'/api/produits/{sample_product}',
                          json={"prix": 0},
                          headers=auth_headers(admin_token))
    assert response.status_code == 400


# --- DELETE /api/produits/<id> ---

def test_delete_product_no_token(client, sample_product):
    response = client.delete(f'/api/produits/{sample_product}')
    assert response.status_code == 401


def test_delete_product_client_forbidden(client, sample_product, client_token):
    response = client.delete(f'/api/produits/{sample_product}',
                             headers=auth_headers(client_token))
    assert response.status_code == 403


def test_delete_product_admin(client, sample_product, admin_token):
    response = client.delete(f'/api/produits/{sample_product}',
                             headers=auth_headers(admin_token))
    assert response.status_code == 200
    assert "supprimé" in response.get_json()["message"]


def test_delete_product_not_found(client, admin_token):
    response = client.delete('/api/produits/9999',
                             headers=auth_headers(admin_token))
    assert response.status_code == 404


def test_delete_product_no_longer_accessible(  # noqa: E501
        client, sample_product, admin_token):
    client.delete(f'/api/produits/{sample_product}',
                  headers=auth_headers(admin_token))
    response = client.get(f'/api/produits/{sample_product}')
    assert response.status_code == 404
