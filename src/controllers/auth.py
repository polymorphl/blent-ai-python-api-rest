from flask_jwt_extended import create_access_token
from ..models import User, Role
from ..extensions import db


def register_user(payload: dict) -> tuple[dict, int]:
    email = (payload.get('email') or '').lower()
    password = payload.get('password') or ''
    name = payload.get('name') or ''

    if not email or not password or not name:
        return {"error": "'email', 'name', 'password' sont obligatoires."}, 400

    if User.find_one(email):
        return {"error": "Un utilisateur existe déjà avec cet email."}, 400

    user = User(email=email, nom=name, role=Role.CLIENT)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return {"message": "Utilisateur créé avec succès"}, 201


def login_user(payload: dict) -> tuple[dict, int]:
    email = (payload.get('email') or '').lower()
    password = payload.get('password') or ''

    if not email or not password:
        return {"error": "'email', 'password' sont obligatoires."}, 400

    user = User.find_one(email)
    if not user or not user.check_password(password):
        return {"error": "Identifiants invalides"}, 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value}
    )
    return {"access_token": token}, 200
