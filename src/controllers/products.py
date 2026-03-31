from ..models import Product
from ..extensions import db


def _serialize(product: Product) -> dict:
    return {
        "id": product.id,
        "nom": product.nom,
        "description": product.description,
        "categorie": product.categorie,
        "prix": product.prix,
        "quantite_stock": product.quantite_stock,
        "date_creation": product.date_creation.isoformat(),
    }


def get_all_products(search: str | None) -> tuple[dict, int]:
    if search:
        products = Product.query.filter(
            db.or_(
                Product.nom.ilike(f"%{search}%"),
                Product.categorie.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        ).all()
    else:
        products = Product.query.all()
    return {"products": [_serialize(p) for p in products]}, 200


def get_product_by_id(product_id: int) -> tuple[dict, int]:
    product = db.session.get(Product, product_id)
    if not product:
        return {"error": "Produit introuvable."}, 404
    return _serialize(product), 200


def create_product(payload: dict) -> tuple[dict, int]:
    nom = (payload.get("nom") or "").strip()
    categorie = (payload.get("categorie") or "").strip()
    prix_raw = payload.get("prix")
    description = payload.get("description") or None

    if not nom:
        return {"error": "'nom' est obligatoire."}, 400
    if not categorie:
        return {"error": "'categorie' est obligatoire."}, 400
    if prix_raw is None:
        return {"error": "'prix' est obligatoire."}, 400

    try:
        prix = float(prix_raw)
        if prix <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return {"error": "'prix' doit être un nombre positif."}, 400

    quantite_raw = payload.get("quantite_stock", 0)
    try:
        quantite_stock = int(quantite_raw)
        if quantite_stock < 0:
            raise ValueError
    except (ValueError, TypeError):
        return {"error": "'quantite_stock' doit être un entier positif ou nul."}, 400  # noqa: E501

    product = Product(
        nom=nom,
        description=description,
        categorie=categorie,
        prix=prix,
        quantite_stock=quantite_stock,
    )
    db.session.add(product)
    db.session.commit()
    return _serialize(product), 201


def update_product(product_id: int, payload: dict) -> tuple[dict, int]:
    product = db.session.get(Product, product_id)
    if not product:
        return {"error": "Produit introuvable."}, 404

    if "nom" in payload:
        nom = (payload["nom"] or "").strip()
        if not nom:
            return {"error": "'nom' ne peut pas être vide."}, 400
        product.nom = nom

    if "categorie" in payload:
        categorie = (payload["categorie"] or "").strip()
        if not categorie:
            return {"error": "'categorie' ne peut pas être vide."}, 400
        product.categorie = categorie

    if "prix" in payload:
        try:
            prix = float(payload["prix"])
            if prix <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return {"error": "'prix' doit être un nombre positif."}, 400
        product.prix = prix

    if "description" in payload:
        product.description = payload["description"] or None

    if "quantite_stock" in payload:
        try:
            quantite_stock = int(payload["quantite_stock"])
            if quantite_stock < 0:
                raise ValueError
        except (ValueError, TypeError):
            return {"error": "'quantite_stock' doit être un entier positif ou nul."}, 400  # noqa: E501
        product.quantite_stock = quantite_stock

    db.session.commit()
    return _serialize(product), 200


def delete_product(product_id: int) -> tuple[dict, int]:
    product = db.session.get(Product, product_id)
    if not product:
        return {"error": "Produit introuvable."}, 404
    db.session.delete(product)
    db.session.commit()
    return {"message": "Produit supprimé avec succès."}, 200
