from flask import Blueprint, request
from ..controllers import products as products_controller
from ..lib.response import success, error
from ..lib.decorators import admin_required

products_bp = Blueprint('products', __name__, url_prefix='/api/produits')


@products_bp.route('', methods=['GET'])
def list_products():
    """
    Retourne la liste de tous les produits, avec filtrage optionnel 
    par recherche textuelle.
    """
    search = request.args.get('search', '').strip() or None
    data, status = products_controller.get_all_products(search)
    return success(data, status) if status < 400 else error(data["error"], status)  # noqa: E501


@products_bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    """Retourne un produit par son identifiant."""
    data, status = products_controller.get_product_by_id(id)
    return success(data, status) if status < 400 else error(data["error"], status)  # noqa: E501


@products_bp.route('', methods=['POST'])
@admin_required
def create_product():
    """Crée un nouveau produit. Réservé aux administrateurs."""
    data, status = products_controller.create_product(request.get_json() or {})
    return success(data, status) if status < 400 else error(data["error"], status)  # noqa: E501


@products_bp.route('/<int:id>', methods=['PATCH'])
@admin_required
def update_product(id):
    """
    Met à jour un produit existant par son identifiant.
    Réservé aux administrateurs.
    """
    payload = request.get_json() or {}
    data, status = products_controller.update_product(id, payload)
    return success(data, status) if status < 400 else error(data["error"], status)  # noqa: E501


@products_bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_product(id):
    """Supprime un produit par son identifiant. Réservé aux administrateurs."""
    data, status = products_controller.delete_product(id)
    return success(data, status) if status < 400 else error(data["error"], status)  # noqa: E501
