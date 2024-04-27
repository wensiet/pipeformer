import httpx

from src import settings
from src.integrations.timeweb.dto import CreateServerRequest, OS, Preset, Compute


class TimewebWrapper:

    def __init__(self):
        self._client = httpx.Client()
        self._endpoint = settings.ProvisionerSettings.host
        self._token = settings.ProvisionerSettings.token

    def create_ssh_key(self, name: str, public_key: str):
        response = self._client.post(
            url=f"{self._endpoint}/v1/ssh-keys",
            headers={"Authorization": f"Bearer {self._token}"},
            json={
                "body": public_key,
                "is_default": False,
                "name": name
            },
        )
        response.raise_for_status()

        return response.json()["ssh_key"]["id"]

    def create_compute(self, name: str, preset: str, os: str, ssh_keys: list[int]):
        request = CreateServerRequest(
            is_ddos_guard=False,
            os_id=OS.get_os(os),
            preset_id=Preset.get_preset(preset),
            bandwidth=200,
            name=name,
            ssh_keys_ids=ssh_keys
        )
        response = self._client.post(
            url=f"{self._endpoint}/v1/servers",
            headers={"Authorization": f"Bearer {self._token}"},
            json=request.dict(exclude_unset=True),
            timeout=60
        )
        response.raise_for_status()

        return Compute.parse_obj(response.json()["server"])

    def get_compute(self, compute_id: int) -> Compute:
        response = self._client.get(
            url=f"{self._endpoint}/v1/servers/{compute_id}",
            headers={"Authorization": f"Bearer {self._token}"},
        )
        response.raise_for_status()

        return Compute.parse_obj(response.json()["server"])

    def delete_compute(self, compute_id: int):
        response = self._client.delete(
            url=f"{self._endpoint}/v1/servers/{compute_id}",
            headers={"Authorization": f"Bearer {self._token}"},
        )
        response.raise_for_status()

    def list_computes(self):
        response = self._client.get(
            url=f"{self._endpoint}/v1/servers",
            headers={"Authorization": f"Bearer {self._token}"},
        )
        response.raise_for_status()

        return [Compute.parse_obj(server) for server in response.json()["servers"]]

