from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from ..models import Role
from .response import error


def login_required(fn):
    # Vérifie que le token JWT est valide
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return error("Token manquant ou invalide.", 401)
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    # Vérifie que le token JWT est valide et que l'utilisateur est admin
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return error("Token manquant ou invalide.", 401)
        if get_jwt().get("role") != Role.ADMIN.value:
            return error("Accès refusé : droits administrateur requis.", 403)
        return fn(*args, **kwargs)
    return wrapper
