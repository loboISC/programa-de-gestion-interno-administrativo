from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import settings
from backend.routes.auth_routes import auth_bp
from backend.routes.vault_routes import vault_bp
from backend.services.auth_service import AuthService
from backend.services.system_service import SystemService
from backend.services.vault_service import VaultService, VaultServiceError
from database.connection import init_engine


def create_app() -> Flask:
    init_engine(settings.database_url)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.app_secret_key
    app.config["auth_service"] = AuthService(
        default_username=settings.default_username,
        session_timeout_minutes=settings.session_timeout_minutes,
    )
    app.config["vault_service"] = VaultService()
    app.config["system_service"] = SystemService()

    CORS(app)

    @app.get("/api/health")
    def health():
        app.config["system_service"].ping_database()
        return jsonify({"ok": True, "database": "connected"}), 200

    @app.errorhandler(VaultServiceError)
    def handle_vault_error(error: VaultServiceError):
        return jsonify({"ok": False, "message": str(error)}), 400

    app.register_blueprint(auth_bp)
    app.register_blueprint(vault_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=settings.app_host, port=settings.app_port, debug=settings.app_debug)
