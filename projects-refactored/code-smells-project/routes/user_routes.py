from flask import Blueprint, request, jsonify
from middlewares.auth import require_auth
from controllers import user_controller

user_bp = Blueprint("usuarios", __name__)


@user_bp.route("/usuarios", methods=["GET"])
@require_auth
def listar_usuarios():
    return jsonify({"dados": user_controller.list_all(), "sucesso": True}), 200


@user_bp.route("/usuarios/<int:user_id>", methods=["GET"])
@require_auth
def buscar_usuario(user_id):
    return jsonify({"dados": user_controller.get_one(user_id), "sucesso": True}), 200


@user_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400
    return jsonify({"dados": user_controller.create(data), "sucesso": True}), 201


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400
    email = (data.get("email") or "").strip()
    senha = data.get("senha") or ""
    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400
    return jsonify({"dados": user_controller.login(email, senha), "sucesso": True}), 200
