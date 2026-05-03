from flask import Blueprint, jsonify
from middlewares.auth import require_admin
from controllers import report_controller

report_bp = Blueprint("relatorios", __name__)


@report_bp.route("/relatorios/vendas", methods=["GET"])
@require_admin
def relatorio_vendas():
    return jsonify({"dados": report_controller.get_sales_report(), "sucesso": True}), 200
