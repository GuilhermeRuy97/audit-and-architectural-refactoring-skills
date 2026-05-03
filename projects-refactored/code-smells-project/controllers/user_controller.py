import logging
import jwt
from datetime import datetime, timedelta, timezone
from config.settings import SECRET_KEY
from middlewares.error_handler import ValidationError, NotFoundError, AuthError
from models import user_model

logger = logging.getLogger(__name__)

TOKEN_EXPIRY_HOURS = 24


def list_all():
    return user_model.get_all()


def get_one(user_id):
    user = user_model.get_by_id(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    return user


def create(data):
    nome = (data.get("nome") or "").strip()
    email = (data.get("email") or "").strip()
    senha = data.get("senha") or ""
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    user_id = user_model.create(nome, email, senha, data.get("tipo", "cliente"))
    logger.info("Usuário criado: email=%s", email)
    return user_model.get_by_id(user_id)


def login(email, senha):
    user_row = user_model.get_by_email(email)
    if not user_row or not user_model.verify_password(user_row, senha):
        raise AuthError("Email ou senha inválidos")
    payload = {
        "sub": user_row["id"],
        "tipo": user_row["tipo"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    logger.info("Login: email=%s", email)
    return {
        "token": token,
        "usuario": {
            "id": user_row["id"],
            "nome": user_row["nome"],
            "email": user_row["email"],
            "tipo": user_row["tipo"],
        },
    }
