from flask import Blueprint, request, jsonify
from middlewares.auth import require_auth
from controllers import product_controller

product_bp = Blueprint("produtos", __name__)


@product_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    return jsonify({"dados": product_controller.list_all(), "sucesso": True}), 200


@product_bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min", type=float)
    preco_max = request.args.get("preco_max", type=float)
    results = product_controller.search(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": results, "total": len(results), "sucesso": True}), 200


@product_bp.route("/produtos/<int:product_id>", methods=["GET"])
def buscar_produto(product_id):
    return jsonify({"dados": product_controller.get_one(product_id), "sucesso": True}), 200


@product_bp.route("/produtos", methods=["POST"])
@require_auth
def criar_produto():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400
    return jsonify({"dados": product_controller.create(data), "sucesso": True}), 201


@product_bp.route("/produtos/<int:product_id>", methods=["PUT"])
@require_auth
def atualizar_produto(product_id):
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400
    return jsonify({"dados": product_controller.update(product_id, data), "sucesso": True}), 200


@product_bp.route("/produtos/<int:product_id>", methods=["DELETE"])
@require_auth
def deletar_produto(product_id):
    product_controller.delete(product_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
