from flask import Blueprint, jsonify, request

from controllers.task_controller import (
    create_task, delete_task, get_all_tasks, get_stats,
    get_task_by_id, search_tasks, update_task,
)
from middlewares.auth import require_auth

task_bp = Blueprint('tasks', __name__)


# Static routes registered before parameterised ones to avoid any ambiguity
@task_bp.route('/tasks/search', methods=['GET'])
@require_auth
def search_tasks_route():
    filters = {
        'q': request.args.get('q', ''),
        'status': request.args.get('status', ''),
        'priority': request.args.get('priority', ''),
        'user_id': request.args.get('user_id', ''),
    }
    return jsonify(search_tasks(filters)), 200


@task_bp.route('/tasks/stats', methods=['GET'])
@require_auth
def task_stats():
    return jsonify(get_stats()), 200


@task_bp.route('/tasks', methods=['GET'])
@require_auth
def get_tasks():
    return jsonify(get_all_tasks()), 200


@task_bp.route('/tasks', methods=['POST'])
@require_auth
def create_task_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(create_task(data)), 201


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
@require_auth
def get_task(task_id):
    return jsonify(get_task_by_id(task_id)), 200


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@require_auth
def update_task_route(task_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(update_task(task_id, data)), 200


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@require_auth
def delete_task_route(task_id):
    delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200
