import httpx

from src.settings import VaultSettings


class VaultSecretExtractor:
    def __init__(self):
        self.vault_settings = VaultSettings()
        self._client = httpx.Client()

    @staticmethod
    def decode_secret(value: str):
        value = value.replace("vault@", "").split(".")
        secret_path = value[0]
        json_path = value[1:]
        return secret_path, json_path

    @staticmethod
    def dict_extractor(data: dict, json_path: list):
        for key in json_path:
            data = data[key]
        return data

    def _authorized_request(self, method, url, body=None):
        return self._client.request(
                method,
                url,
                headers={"X-Vault-Token": self.vault_settings.token},
                json=body,
        )

    def get_secret(self, secret_key: str):
        secret_path, json_path = self.decode_secret(secret_key)
        response = self._authorized_request(
                "GET",
                f"{self.vault_settings.host}/v1/{self.vault_settings.secrets_home}/data/{secret_path}"
        )
        response.raise_for_status()
        value = self.dict_extractor(response.json()["data"]["data"], json_path)
        return value
