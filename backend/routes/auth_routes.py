from flask import Blueprint, current_app, jsonify, request

from backend.services.auth_service import AuthenticationError, AuthService, RegistrationError

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    service: AuthService = current_app.config["auth_service"]

    try:
        result = service.login(
            username=payload.get("username", ""),
            password=payload.get("password", ""),
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
    except AuthenticationError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 401

    return jsonify({"ok": True, **result}), 200


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    service: AuthService = current_app.config["auth_service"]

    try:
        result = service.register_user(payload)
    except RegistrationError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

    return jsonify({"ok": True, "user": result}), 201


@auth_bp.get("/session")
def validate_session():
    service: AuthService = current_app.config["auth_service"]
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    session = service.validate_session(token)
    if not session:
        return jsonify({"ok": False, "message": "Sesion invalida o expirada."}), 401
    return jsonify({"ok": True, "user": session}), 200
