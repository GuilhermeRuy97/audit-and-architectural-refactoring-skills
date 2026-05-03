from flask import Blueprint, request, jsonify, g
from middlewares.auth import require_auth
from controllers import order_controller

order_bp = Blueprint("pedidos", __name__)


@order_bp.route("/pedidos", methods=["POST"])
@require_auth
def criar_pedido():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400
    usuario_id = data.get("usuario_id") or g.current_user_id
    itens = data.get("itens", [])
    resultado = order_controller.create(usuario_id, itens)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


@order_bp.route("/pedidos", methods=["GET"])
@require_auth
def listar_todos_pedidos():
    return jsonify({"dados": order_controller.list_all(), "sucesso": True}), 200


@order_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
@require_auth
def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": order_controller.list_by_user(usuario_id), "sucesso": True}), 200


@order_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
@require_auth
def atualizar_status_pedido(pedido_id):
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400
    order_controller.update_status(pedido_id, data.get("status", ""))
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
