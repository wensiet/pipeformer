import os

import httpx

from src.services.utils import url_encode
from src.settings import GrafanaSettings


class GrafanaWrapper:

    def __init__(self):
        self.grafana_settings = GrafanaSettings()
        self._token = os.getenv("GRAFANA_API_TOKEN")
        self._client = httpx.Client()

    def refresh_datasource(self):
        request = {
            "id": 8,
            "uid": "adkp3t7dxa5mob",
            "orgId": 1,
            "name": "zabbix-on-docker",
            "type": "alexanderzobnin-zabbix-datasource",
            "typeLogoUrl": "public/plugins/alexanderzobnin-zabbix-datasource/img/icn-zabbix-datasource.svg",
            "access": "proxy",
            "url": "http://185.154.194.142:8080/api_jsonrpc.php",
            "user": "",
            "database": "",
            "basicAuth": False,
            "basicAuthUser": "",
            "withCredentials": False,
            "isDefault": True,
            "jsonData": {
                "authType": "userLogin",
                "trends": True,
                "trendsFrom": "",
                "trendsRange": "",
                "cacheTTL": "",
                "disableDataAlignment": False,
                "username": "Admin"
            },
            "secureJsonFields": {
                "password": True
            },
            "readOnly": False,
            "accessControl": {
                "alert.instances.external:read": True,
                "alert.instances.external:write": True,
                "alert.notifications.external:read": True,
                "alert.notifications.external:write": True,
                "alert.rules.external:read": True,
                "alert.rules.external:write": True,
                "datasources.id:read": True,
                "datasources:delete": True,
                "datasources:query": True,
                "datasources:read": True,
                "datasources:write": True
            }
        }
        response = self._client.request("PUT",
                                        f"{self.grafana_settings.host}/api/datasources/uid/adkp3t7dxa5mob",
                                        headers={"Authorization": f"Bearer {self._token}"},
                                        json=request)
        response.raise_for_status()

    def make_dashboard_link(self, compute_name):
        return (f"{self.grafana_settings.host}/d/"
                f"{self.grafana_settings.folder_uid}/"
                f"{self.grafana_settings.base_dashboard}?"
                f"orgId=1&var-Group={url_encode(self.grafana_settings.zabbix_group)}"
                f"&var-Host={compute_name}")
