from flask import Blueprint, request
from ..controllers import auth as auth_controller
from ..lib.response import success, error

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Inscription d'un nouvel utilisateur.

    Body JSON:
        email (str): Email unique de l'utilisateur
        password (str): Mot de passe
        name (str): Nom de l'utilisateur
        role (str): Role de l'utilisateur

    Returns:
        201: Utilisateur créé avec succès
        400: Champs manquants ou email déjà utilisé
    """
    data, status = auth_controller.register_user(request.get_json() or {})
    return (success(data, status) if status < 400 else error(data["error"], status))


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Connexion d'un utilisateur.

    Body JSON:
        email (str): Email unique de l'utilisateur
        password (str): Mot de passe

    Returns:
        200: JWT généré
        400: Payload invalide
        401: Identifiants invalides
    """
    data, status = auth_controller.login_user(request.get_json() or {})
    return (success(data, status) if status < 400 else error(data["error"], status))
