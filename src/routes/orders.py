from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, get_jwt
from ..controllers import orders as orders_controller
from ..lib.response import success, error
from ..lib.decorators import login_required, admin_required
from ..models import Role

orders_bp = Blueprint('orders', __name__, url_prefix='/api/commandes')


def _current_user():
    """Retourne (user_id, is_admin) depuis le JWT courant."""
    user_id = int(get_jwt_identity())
    is_admin = get_jwt().get("role") == Role.ADMIN.value
    return user_id, is_admin


@orders_bp.route('', methods=['GET'])
@login_required
def list_orders():
    """Retourne les commandes. Admin voit tout, client voit les siennes."""
    user_id, is_admin = _current_user()
    data, status = orders_controller.get_all_orders(user_id, is_admin)
    return success(data, status) if status < 400 else error(data["error"], status)  # noqa: E501


@orders_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_order(id):
    """Retourne une commande par son identifiant."""
    user_id, is_admin = _current_user()
    data, status = orders_controller.get_order_by_id(id, user_id, is_admin)
    return success(data, status) if status < 400 else error(data["error"], status)  # noqa: E501


@orders_bp.route('', methods=['POST'])
@login_required
def create_order():
    """Crée une nouvelle commande pour l'utilisateur connecté."""
    user_id, _ = _current_user()
    data, status = orders_controller.create_order(
        request.get_json() or {}, user_id)
    return success(data, status) if status < 400 else error(data["error"], status)  # noqa: E501


@orders_bp.route('/<int:id>', methods=['PATCH'])
@admin_required
def update_order_status(id):
    """Modifie le statut d'une commande. Réservé aux administrateurs."""
    data, status = orders_controller.update_order_status(
        id, request.get_json() or {})
    return success(data, status) if status < 400 else error(data["error"], status)  # noqa: E501


@orders_bp.route('/<int:id>/lignes', methods=['GET'])
@login_required
def get_order_lines(id):
    """Retourne les lignes d'une commande."""
    user_id, is_admin = _current_user()
    data, status = orders_controller.get_order_lines(id, user_id, is_admin)
    return success(data, status) if status < 400 else error(data["error"], status)  # noqa: E501
