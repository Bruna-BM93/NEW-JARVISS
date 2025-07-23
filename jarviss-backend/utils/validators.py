from flask_jwt_extended import get_jwt_identity
from functools import wraps
from flask import jsonify
from models.user import User

def require_plano(planos_permitidos):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.plano not in planos_permitidos:
                return jsonify({'erro': f'Esta funcionalidade está disponível apenas para os planos: {", ".join(planos_permitidos)}'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
