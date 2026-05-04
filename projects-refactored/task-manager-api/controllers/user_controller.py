import logging
from datetime import datetime, timedelta

import jwt

from config.settings import JWT_EXPIRY_HOURS, SECRET_KEY
from database import db
from middlewares.error_handler import AuthError, NotFoundError, ValidationError
from models.task import Task
from models.user import User
from utils.helpers import MIN_PASSWORD_LENGTH, VALID_ROLES, validate_email

logger = logging.getLogger(__name__)


def get_all_users() -> list:
    from sqlalchemy import func, select
    rows = db.session.execute(
        select(User, func.count(Task.id).label('task_count'))
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id)
    ).all()
    return [
        {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'active': user.active,
            'created_at': str(user.created_at),
            'task_count': task_count,
        }
        for user, task_count in rows
    ]


def get_user_by_id(user_id: int) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in user.tasks]
    return data


def create_user(data: dict) -> dict:
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    role = data.get('role', 'user')

    if not name:
        raise ValidationError('Nome é obrigatório')
    if not email:
        raise ValidationError('Email é obrigatório')
    if not password:
        raise ValidationError('Senha é obrigatória')
    if not validate_email(email):
        raise ValidationError('Email inválido')
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
    if role not in VALID_ROLES:
        raise ValidationError('Role inválido')
    if User.query.filter_by(email=email).first():
        raise ValidationError('Email já cadastrado')

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    db.session.add(user)
    db.session.commit()
    logger.info('User created: %d - %s', user.id, user.name)
    return user.to_dict()


def update_user(user_id: int, data: dict) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')

    if 'name' in data:
        user.name = (data['name'] or '').strip()

    if 'email' in data:
        email = (data['email'] or '').strip()
        if not validate_email(email):
            raise ValidationError('Email inválido')
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user_id:
            raise ValidationError('Email já cadastrado')
        user.email = email

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            raise ValidationError('Senha muito curta')
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            raise ValidationError('Role inválido')
        user.role = data['role']

    if 'active' in data:
        user.active = bool(data['active'])

    db.session.commit()
    return user.to_dict()


def delete_user(user_id: int) -> None:
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    logger.info('User deleted: %d', user_id)


def login(data: dict) -> dict:
    email = data.get('email', '')
    password = data.get('password', '')

    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise AuthError('Credenciais inválidas')
    if not user.active:
        raise AuthError('Usuário inativo')

    payload = {
        'sub': user.id,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': token,
    }


def get_user_tasks(user_id: int) -> list:
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    return [t.to_dict() for t in user.tasks]
