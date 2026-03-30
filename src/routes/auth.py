from flask import Blueprint, request
from ..models import User, Role
from ..extensions import db
from flask_jwt_extended import create_access_token
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
    payload = request.get_json() or {}
    email = (payload.get('email') or '').lower()
    password = payload.get('password') or ''
    name = payload.get('name') or ''
    role = Role.CLIENT

    if not email or not password or not name:
        return error(
            "'email', 'name', 'password' sont obligatoires.",
            400
        )

    if User.find_one(email):
        return error(
            "Un utilisateur existe déjà avec cet email.",
            400
        )

    user = User(email=email, nom=name, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return success(
        {"message": "Utilisateur créé avec succès"},
        201
    )


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Connexion d'un utilisateur.

    Body JSON:
        email (str): Email unique de l'utilisateur
        password (str): Mot de passe

    Returns:
        200: JWT généré
        400: Payload ou identifiants invalides
    """
    payload = request.get_json() or {}
    email = (payload.get('email') or '').lower()
    password = payload.get('password') or ''

    if not email or not password:
        return error(
            "'email', 'password' sont obligatoires.",
            400
        )

    user = User.find_one(email)
    if not user or not user.check_password(password=password):
        return error(
            "Identifiants invalides",
            400
        )
    token = create_access_token(identity=str(
        user.id), additional_claims={"role": user.role.value})

    return success({"access_token": token}, 200)
