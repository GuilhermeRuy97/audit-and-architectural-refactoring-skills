from functools import wraps
from flask import request, jsonify, g
import jwt
from config.settings import SECRET_KEY


def _decode_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, "Token de autenticação obrigatório"
    token = auth_header[7:]
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"]), None
    except jwt.ExpiredSignatureError:
        return None, "Token expirado"
    except jwt.InvalidTokenError:
        return None, "Token inválido"


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload, err = _decode_token()
        if err:
            return jsonify({"erro": err, "sucesso": False}), 401
        g.current_user_id = payload["sub"]
        g.current_user_tipo = payload.get("tipo", "cliente")
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload, err = _decode_token()
        if err:
            return jsonify({"erro": err, "sucesso": False}), 401
        g.current_user_id = payload["sub"]
        g.current_user_tipo = payload.get("tipo", "cliente")
        if g.current_user_tipo != "admin":
            return jsonify({"erro": "Acesso restrito a administradores", "sucesso": False}), 403
        return f(*args, **kwargs)
    return decorated
