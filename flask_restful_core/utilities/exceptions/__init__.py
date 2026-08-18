
from flask import jsonify


def register_handlers(app):
    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify(message=str(e.description) or '', code=str(e.code) or '500'), 500
