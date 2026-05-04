import logging
from datetime import datetime, timedelta

from sqlalchemy import case, func, select

from database import db
from middlewares.error_handler import NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import calculate_percentage

logger = logging.getLogger(__name__)


def get_summary() -> dict:
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    p1 = Task.query.filter_by(priority=1).count()
    p2 = Task.query.filter_by(priority=2).count()
    p3 = Task.query.filter_by(priority=3).count()
    p4 = Task.query.filter_by(priority=4).count()
    p5 = Task.query.filter_by(priority=5).count()

    overdue_tasks = [t for t in Task.query.all() if t.is_overdue()]
    overdue_list = [
        {
            'id': t.id,
            'title': t.title,
            'due_date': str(t.due_date),
            'days_overdue': (datetime.utcnow() - t.due_date).days,
        }
        for t in overdue_tasks
    ]

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done',
        Task.updated_at >= seven_days_ago,
    ).count()

    # Single aggregate query — fixes N+1 (one query per user in original)
    rows = db.session.execute(
        select(
            User.id.label('user_id'),
            User.name.label('user_name'),
            func.count(Task.id).label('total'),
            func.sum(case((Task.status == 'done', 1), else_=0)).label('completed'),
        )
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id, User.name)
    ).all()

    user_stats = [
        {
            'user_id': row.user_id,
            'user_name': row.user_name,
            'total_tasks': row.total or 0,
            'completed_tasks': row.completed or 0,
            'completion_rate': calculate_percentage(row.completed or 0, row.total or 0),
        }
        for row in rows
    ]

    return {
        'generated_at': str(datetime.utcnow()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': {
            'critical': p1,
            'high': p2,
            'medium': p3,
            'low': p4,
            'minimal': p5,
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def get_user_report(user_id: int) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = sum(1 for t in tasks if t.status == 'done')
    pending = sum(1 for t in tasks if t.status == 'pending')
    in_progress = sum(1 for t in tasks if t.status == 'in_progress')
    cancelled = sum(1 for t in tasks if t.status == 'cancelled')
    overdue = sum(1 for t in tasks if t.is_overdue())
    high_priority = sum(1 for t in tasks if t.priority <= 2)

    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': calculate_percentage(done, total),
        },
    }


def get_categories() -> list:
    categories = Category.query.all()
    return [
        {**c.to_dict(), 'task_count': Task.query.filter_by(category_id=c.id).count()}
        for c in categories
    ]


def create_category(data: dict) -> dict:
    name = (data.get('name') or '').strip()
    if not name:
        raise ValidationError('Nome é obrigatório')
    cat = Category()
    cat.name = name
    cat.description = data.get('description', '')
    cat.color = data.get('color', '#000000')
    db.session.add(cat)
    db.session.commit()
    return cat.to_dict()


def update_category(cat_id: int, data: dict) -> dict:
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise NotFoundError('Categoria não encontrada')
    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']
    db.session.commit()
    return cat.to_dict()


def delete_category(cat_id: int) -> None:
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise NotFoundError('Categoria não encontrada')
    db.session.delete(cat)
    db.session.commit()
