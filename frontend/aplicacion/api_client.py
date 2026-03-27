from __future__ import annotations

from dataclasses import dataclass, field

import requests


@dataclass
class ApiClient:
    base_url: str = "http://127.0.0.1:5000/api"
    timeout: int = 10
    session: requests.Session = field(default_factory=requests.Session)
    auth_token: str | None = None

    def __post_init__(self):
        self.session.headers.update({"Content-Type": "application/json"})

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            message = None
            try:
                message = response.json().get("message")
            except ValueError:
                message = response.text or str(exc)
            raise RuntimeError(message or str(exc)) from exc

    def get(self, path: str, **kwargs):
        return self.session.get(f"{self.base_url}{path}", timeout=self.timeout, **kwargs)

    def post(self, path: str, **kwargs):
        return self.session.post(f"{self.base_url}{path}", timeout=self.timeout, **kwargs)

    def put(self, path: str, **kwargs):
        return self.session.put(f"{self.base_url}{path}", timeout=self.timeout, **kwargs)

    def delete(self, path: str, **kwargs):
        return self.session.delete(f"{self.base_url}{path}", timeout=self.timeout, **kwargs)

    def set_token(self, token: str | None) -> None:
        self.auth_token = token
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            self.session.headers.pop("Authorization", None)

    def health(self) -> dict:
        response = self.get("/health")
        self._raise_for_status(response)
        return response.json()

    def login(self, username: str, password: str) -> dict:
        response = self.post("/auth/login", json={"username": username, "password": password})
        self._raise_for_status(response)
        payload = response.json()
        self.set_token(payload["token"])
        return payload

    def register_user(self, payload: dict) -> dict:
        response = self.post("/auth/register", json=payload)
        self._raise_for_status(response)
        return response.json()["user"]

    def list_hosting_providers(self, query: str = "") -> list[dict]:
        response = self.get("/hosting/providers", params={"q": query})
        self._raise_for_status(response)
        return response.json()["items"]

    def create_hosting_provider(self, payload: dict) -> dict:
        response = self.post("/hosting/providers", json=payload)
        self._raise_for_status(response)
        return response.json()["item"]

    def delete_hosting_provider(self, provider_id: str) -> None:
        response = self.delete(f"/hosting/providers/{provider_id}")
        self._raise_for_status(response)

    def list_credentials(self, query: str = "") -> list[dict]:
        response = self.get("/vault/credentials", params={"q": query})
        self._raise_for_status(response)
        return response.json()["items"]

    def create_credential(self, payload: dict) -> dict:
        response = self.post("/vault/credentials", json=payload)
        self._raise_for_status(response)
        return response.json()["item"]

    def update_credential(self, credential_id: str, payload: dict) -> dict:
        response = self.put(f"/vault/credentials/{credential_id}", json=payload)
        self._raise_for_status(response)
        return response.json()["item"]

    def delete_credential(self, credential_id: str) -> None:
        response = self.delete(f"/vault/credentials/{credential_id}")
        self._raise_for_status(response)
