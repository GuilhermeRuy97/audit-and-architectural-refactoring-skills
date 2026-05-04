from functools import wraps

import jwt
from flask import g, request

from config.settings import SECRET_KEY
from middlewares.error_handler import AuthError


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthError('Token expired')
    except jwt.InvalidTokenError:
        raise AuthError('Invalid token')


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise AuthError('Authentication required')
        payload = _decode_token(auth_header[7:])
        g.current_user_id = payload['sub']
        g.current_user_role = payload.get('role', 'user')
        return f(*args, **kwargs)
    return decorated
