import logging

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


class AuthError(Exception):
    pass


def register_error_handlers(app):
    from flask import jsonify

    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({'error': str(e)}), 404

    @app.errorhandler(ValidationError)
    def handle_validation(e):
        return jsonify({'error': str(e)}), 422

    @app.errorhandler(AuthError)
    def handle_auth(e):
        return jsonify({'error': str(e)}), 401

    @app.errorhandler(Exception)
    def handle_generic(e):
        logger.exception('Unhandled error')
        return jsonify({'error': 'Internal server error'}), 500
