from flask import Blueprint, request
from ..controllers import auth as auth_controller
from ..lib.response import success, error

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur."""
    data, status = auth_controller.register_user(request.get_json() or {})
    return (success(data, status) if status < 400 else error(data["error"], status))  # noqa: E501


@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur."""
    data, status = auth_controller.login_user(request.get_json() or {})
    return (success(data, status) if status < 400 else error(data["error"], status))  # noqa: E501
