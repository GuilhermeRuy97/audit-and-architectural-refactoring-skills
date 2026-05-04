from flask import Blueprint, jsonify, request

from controllers.user_controller import (
    create_user, delete_user, get_all_users, get_user_by_id,
    get_user_tasks, login, update_user,
)
from middlewares.auth import require_auth

user_bp = Blueprint('users', __name__)


@user_bp.route('/login', methods=['POST'])
def login_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(login(data)), 200


@user_bp.route('/users', methods=['POST'])
def create_user_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(create_user(data)), 201


@user_bp.route('/users', methods=['GET'])
@require_auth
def get_users():
    return jsonify(get_all_users()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    return jsonify(get_user_by_id(user_id)), 200


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_auth
def update_user_route(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(update_user(user_id, data)), 200


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_auth
def delete_user_route(user_id):
    delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
@require_auth
def get_user_tasks_route(user_id):
    return jsonify(get_user_tasks(user_id)), 200
