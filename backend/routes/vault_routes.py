from flask import Blueprint, current_app, jsonify, request

from backend.services.vault_service import VaultService

vault_bp = Blueprint("vault", __name__, url_prefix="/api/vault")


def _token_from_header() -> str:
    return request.headers.get("Authorization", "").removeprefix("Bearer ").strip()


@vault_bp.get("/credentials")
def list_credentials():
    service: VaultService = current_app.config["vault_service"]
    items = service.list_credentials(_token_from_header(), request.args.get("q", ""))
    return jsonify({"ok": True, "items": items}), 200


@vault_bp.post("/credentials")
def create_credential():
    service: VaultService = current_app.config["vault_service"]
    payload = request.get_json(silent=True) or {}
    item = service.create_credential(_token_from_header(), payload)
    return jsonify({"ok": True, "item": item}), 201


@vault_bp.put("/credentials/<uuid:credential_id>")
def update_credential(credential_id):
    service: VaultService = current_app.config["vault_service"]
    payload = request.get_json(silent=True) or {}
    item = service.update_credential(_token_from_header(), credential_id, payload)
    return jsonify({"ok": True, "item": item}), 200


@vault_bp.delete("/credentials/<uuid:credential_id>")
def delete_credential(credential_id):
    service: VaultService = current_app.config["vault_service"]
    service.delete_credential(_token_from_header(), credential_id)
    return jsonify({"ok": True}), 200
