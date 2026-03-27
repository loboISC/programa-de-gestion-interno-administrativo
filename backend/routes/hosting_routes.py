from flask import Blueprint, current_app, jsonify, request

from backend.services.hosting_service import HostingService, HostingServiceError

hosting_bp = Blueprint("hosting", __name__, url_prefix="/api/hosting")


def _token_from_header() -> str:
    return request.headers.get("Authorization", "").removeprefix("Bearer ").strip()


@hosting_bp.get("/providers")
def list_providers():
    service: HostingService = current_app.config["hosting_service"]
    items = service.list_providers(_token_from_header(), request.args.get("q", ""))
    return jsonify({"ok": True, "items": items}), 200


@hosting_bp.post("/providers")
def create_provider():
    service: HostingService = current_app.config["hosting_service"]
    payload = request.get_json(silent=True) or {}
    item = service.create_provider(_token_from_header(), payload)
    return jsonify({"ok": True, "item": item}), 201


@hosting_bp.delete("/providers/<uuid:provider_id>")
def delete_provider(provider_id):
    service: HostingService = current_app.config["hosting_service"]
    service.delete_provider(_token_from_header(), provider_id)
    return jsonify({"ok": True}), 200
