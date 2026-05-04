import logging
from datetime import datetime

from sqlalchemy.orm import joinedload

from database import db
from middlewares.error_handler import NotFoundError, ValidationError
from models.category import Category
from models.task import MAX_PRIORITY, MIN_PRIORITY, VALID_STATUSES, Task
from models.user import User
from utils.helpers import MAX_TITLE_LENGTH, MIN_TITLE_LENGTH, parse_date

logger = logging.getLogger(__name__)

_DEFAULT_PRIORITY = 3
_DEFAULT_STATUS = 'pending'


def get_all_tasks() -> list:
    tasks = Task.query.options(
        joinedload(Task.user),
        joinedload(Task.category),
    ).all()
    result = []
    for t in tasks:
        data = t.to_dict()
        data['user_name'] = t.user.name if t.user else None
        data['category_name'] = t.category.name if t.category else None
        result.append(data)
    return result


def get_task_by_id(task_id: int) -> dict:
    task = db.session.get(Task, task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    return task.to_dict()


def create_task(data: dict) -> dict:
    title = (data.get('title') or '').strip()
    if not title:
        raise ValidationError('Título é obrigatório')
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')

    status = data.get('status', _DEFAULT_STATUS)
    if status not in VALID_STATUSES:
        raise ValidationError('Status inválido')

    priority = data.get('priority', _DEFAULT_PRIORITY)
    if not (MIN_PRIORITY <= priority <= MAX_PRIORITY):
        raise ValidationError('Prioridade deve ser entre 1 e 5')

    user_id = data.get('user_id')
    if user_id and not db.session.get(User, user_id):
        raise NotFoundError('Usuário não encontrado')

    category_id = data.get('category_id')
    if category_id and not db.session.get(Category, category_id):
        raise NotFoundError('Categoria não encontrada')

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date_raw = data.get('due_date')
    if due_date_raw:
        parsed = parse_date(due_date_raw)
        if not parsed:
            raise ValidationError('Formato de data inválido. Use YYYY-MM-DD')
        task.due_date = parsed

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    logger.info('Task created: %d - %s', task.id, task.title)
    return task.to_dict()


def update_task(task_id: int, data: dict) -> dict:
    task = db.session.get(Task, task_id)
    if not task:
        raise NotFoundError('Task não encontrada')

    if 'title' in data:
        title = (data['title'] or '').strip()
        if len(title) < MIN_TITLE_LENGTH:
            raise ValidationError('Título muito curto')
        if len(title) > MAX_TITLE_LENGTH:
            raise ValidationError('Título muito longo')
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            raise ValidationError('Status inválido')
        task.status = data['status']

    if 'priority' in data:
        if not (MIN_PRIORITY <= data['priority'] <= MAX_PRIORITY):
            raise ValidationError('Prioridade deve ser entre 1 e 5')
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not db.session.get(User, data['user_id']):
            raise NotFoundError('Usuário não encontrado')
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not db.session.get(Category, data['category_id']):
            raise NotFoundError('Categoria não encontrada')
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            parsed = parse_date(data['due_date'])
            if not parsed:
                raise ValidationError('Formato de data inválido')
            task.due_date = parsed
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = datetime.utcnow()
    db.session.commit()
    logger.info('Task updated: %d', task.id)
    return task.to_dict()


def delete_task(task_id: int) -> None:
    task = db.session.get(Task, task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    db.session.delete(task)
    db.session.commit()
    logger.info('Task deleted: %d', task_id)


def search_tasks(filters: dict) -> list:
    query = Task.query

    if filters.get('q'):
        q = filters['q']
        query = query.filter(
            db.or_(
                Task.title.like(f'%{q}%'),
                Task.description.like(f'%{q}%'),
            )
        )
    if filters.get('status'):
        query = query.filter(Task.status == filters['status'])
    if filters.get('priority'):
        query = query.filter(Task.priority == int(filters['priority']))
    if filters.get('user_id'):
        query = query.filter(Task.user_id == int(filters['user_id']))

    return [t.to_dict() for t in query.all()]


def get_stats() -> dict:
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()
    overdue = sum(1 for t in Task.query.all() if t.is_overdue())
    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
