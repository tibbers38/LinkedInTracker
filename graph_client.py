from pathlib import Path

import msal
import requests


class GraphClient:
    GRAPH_URL = "https://graph.microsoft.com/v1.0"
    def __init__(
        self,
        client_id: str,
        tenant_id: str,
        scopes: list[str],
        token_cache: str = "token_cache.bin",
    ):
        self.scopes = scopes
        self.access_token = None
        self.cache = msal.SerializableTokenCache()
        if Path(token_cache).exists():
            self.cache.deserialize(Path(token_cache).read_text())
        self.cache_path = token_cache
        self.app = msal.PublicClientApplication(
            client_id=client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            token_cache=self.cache,
        )

    def authenticate(self):
        accounts = self.app.get_accounts()
        result = None
        if accounts:
            result = self.app.acquire_token_silent(
                self.scopes,
                account=accounts[0]
            )
        if not result:
            result = self.app.acquire_token_interactive(
                scopes=self.scopes
            )
        if "access_token" not in result:
            raise RuntimeError(result)
        self.access_token = result["access_token"]
        if self.cache.has_state_changed:
            Path(self.cache_path).write_text(
                self.cache.serialize()
            )

    def _headers(self):
        if not self.access_token:
            raise RuntimeError(
                "Please call authenticate() first."
            )
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    def me(self):
        response = requests.get(
            f"{self.GRAPH_URL}/me",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def drive(self):
        response = requests.get(
            f"{self.GRAPH_URL}/me/drive",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def list_root(self):
        response = requests.get(
            f"{self.GRAPH_URL}/me/drive/root/children",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()["value"]

    def upload_file(
        self,
        local_path: str,
        remote_path: str,
    ):
        with open(local_path, "rb") as f:
            response = requests.put(
                f"{self.GRAPH_URL}/me/drive/root:/{remote_path}:/content",
                headers=self._headers(),
                data=f,
            )
        response.raise_for_status()
        return response.json()