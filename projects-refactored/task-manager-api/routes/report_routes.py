from flask import Blueprint, jsonify, request

from controllers.report_controller import (
    create_category, delete_category, get_categories,
    get_summary, get_user_report, update_category,
)
from middlewares.auth import require_auth

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
@require_auth
def summary_report():
    return jsonify(get_summary()), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
@require_auth
def user_report(user_id):
    return jsonify(get_user_report(user_id)), 200


@report_bp.route('/categories', methods=['GET'])
@require_auth
def get_categories_route():
    return jsonify(get_categories()), 200


@report_bp.route('/categories', methods=['POST'])
@require_auth
def create_category_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(create_category(data)), 201


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@require_auth
def update_category_route(cat_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(update_category(cat_id, data)), 200


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@require_auth
def delete_category_route(cat_id):
    delete_category(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
