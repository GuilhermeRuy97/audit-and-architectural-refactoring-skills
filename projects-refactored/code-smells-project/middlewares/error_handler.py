import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


class AuthError(Exception):
    pass


def register_error_handlers(app):
    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({"erro": str(e), "sucesso": False}), 404

    @app.errorhandler(ValidationError)
    def handle_validation(e):
        return jsonify({"erro": str(e), "sucesso": False}), 400

    @app.errorhandler(AuthError)
    def handle_auth(e):
        return jsonify({"erro": str(e), "sucesso": False}), 401

    @app.errorhandler(Exception)
    def handle_generic(e):
        if isinstance(e, HTTPException):
            return e
        logger.exception("Unhandled error: %s", e)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
