from ..models import Order, OrderLine, OrderStatus, Product
from ..extensions import db


def _serialize_order(order: Order) -> dict:
    return {
        "id": order.id,
        "utilisateur_id": order.utilisateur_id,
        "date_commande": order.date_commande.isoformat(),
        "adresse_livraison": order.adresse_livraison,
        "statut": order.statut.value,
        "lines_len": len(order.lines),
    }


def _serialize_line(line: OrderLine) -> dict:
    return {
        "id": line.id,
        "produit_id": line.produit_id,
        "nom_produit": line.product.nom,
        "quantite": line.quantite,
        "prix_unitaire": line.prix_unitaire,
    }


def get_all_orders(user_id: int, is_admin: bool) -> tuple[dict, int]:
    if is_admin:
        orders = Order.query.all()
    else:
        orders = Order.query.filter_by(utilisateur_id=user_id).all()
    return {"orders": [_serialize_order(o) for o in orders]}, 200


def get_order_by_id(order_id: int, user_id: int, is_admin: bool) -> tuple[dict, int]:  # noqa: E501
    order = db.session.get(Order, order_id)
    if not order:
        return {"error": "Commande introuvable."}, 404
    if not is_admin and order.utilisateur_id != user_id:
        return {"error": "Accès refusé."}, 403
    return _serialize_order(order), 200


def create_order(payload: dict, user_id: int) -> tuple[dict, int]:
    adresse = (payload.get("adresse_livraison") or "").strip()
    if not adresse:
        return {"error": "'adresse_livraison' est obligatoire."}, 400

    lines_raw = payload.get("lines")
    if not lines_raw or not isinstance(lines_raw, list):
        return {"error": "'lines' est obligatoire et doit être une liste non vide."}, 400  # noqa: E501

    # Valider et résoudre chaque ligne avant toute écriture
    resolved = []
    for i, line in enumerate(lines_raw):
        produit_id = line.get("produit_id")
        quantite_raw = line.get("quantite")

        try:
            produit_id = int(produit_id)
        except (TypeError, ValueError):
            return {"error": f"Ligne {i+1} : 'produit_id' doit être un entier."}, 400  # noqa: E501

        try:
            quantite = int(quantite_raw)
            if quantite <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return {"error": f"Ligne {i+1} : 'quantite' doit être un entier strictement positif."}, 400  # noqa: E501

        product = db.session.get(Product, produit_id)
        if not product:
            return {"error": f"Produit {produit_id} introuvable."}, 404
        if product.quantite_stock < quantite:
            return {"error": f"Stock insuffisant pour le produit '{product.nom}' (disponible : {product.quantite_stock})."}, 400  # noqa: E501

        resolved.append((product, quantite))

    # Créer la commande et les lines, décrémenter le stock
    order = Order(utilisateur_id=user_id, adresse_livraison=adresse)
    db.session.add(order)
    db.session.flush()  # Obtenir order.id avant le commit

    for product, quantite in resolved:
        line = OrderLine(
            commande_id=order.id,
            produit_id=product.id,
            quantite=quantite,
            prix_unitaire=product.prix,
        )
        db.session.add(line)
        product.quantite_stock -= quantite

    db.session.commit()
    return _serialize_order(order), 201


def update_order_status(order_id: int, payload: dict) -> tuple[dict, int]:
    order = db.session.get(Order, order_id)
    if not order:
        return {"error": "Commande introuvable."}, 404

    statut_raw = (payload.get("statut") or "").strip()
    valid_values = [s.value for s in OrderStatus]
    if statut_raw not in valid_values:
        return {"error": f"'statut' invalide. Valeurs acceptées : {valid_values}."}, 400  # noqa: E501

    order.statut = OrderStatus(statut_raw)
    db.session.commit()
    return _serialize_order(order), 200


def get_order_lines(order_id: int, user_id: int, is_admin: bool) -> tuple[dict, int]:  # noqa: E501
    order = db.session.get(Order, order_id)
    if not order:
        return {"error": "Commande introuvable."}, 404
    if not is_admin and order.utilisateur_id != user_id:
        return {"error": "Accès refusé."}, 403
    return {"lines": [_serialize_line(line) for line in order.lines]}, 200
