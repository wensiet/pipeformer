import logging
import os

import httpx


class ZabbixWrapper:
    def __init__(self):
        zabbix_host = os.getenv("ZABBIX_HOST")
        zabbix_port = os.getenv("ZABBIX_PORT", "8080")
        zabbix_schema = os.getenv("ZABBIX_SCHEMA", "http")
        self.endpoint = f"{zabbix_schema}://{zabbix_host}:{zabbix_port}/api_jsonrpc.php"
        self.user = os.getenv("ZABBIX_USER")
        self.password = os.getenv("ZABBIX_PASSWORD")
        self._client = httpx.Client()

    def _authorized_request(self, method, endpoint, body=None):
        auth_payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "username": self.user,
                "password": self.password
            },
            "id": 1
        }
        response = self._client.request(
            "POST",
            url=self.endpoint,
            json=auth_payload
        )
        response.raise_for_status()
        auth_results = response.json()
        if 'error' in auth_results:
            print(auth_results['error']['data'])
            logging.error("Failed to authenticate:", auth_results['error']['data'])
            exit(1)
        auth_token = auth_results['result']
        body["auth"] = auth_token
        return self._client.request(
            method,
            url=endpoint,
            json=body
        )

    def connect_host(self, host: str, name: str):
        new_host = {
            "host": name,
            "interfaces": [{
                "type": 1,  # 1 for agent, 2 for SNMP, 3 for IPMI, 4 for JMX
                "main": 1,
                "useip": 1,
                "ip": host,  # IP address of the host
                "dns": "",
                "port": "10050"  # Agent port
            }],
            "groups": [{
                "groupid": "2"  # Group ID of the host group the new host belongs to
            }],
            "templates": [{
                "templateid": "10001"  # Template ID of the template to be linked with the new host
            }]
        }
        body = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": new_host,
            "id": 1
        }
        result = self._authorized_request("POST", self.endpoint, body)
        result.raise_for_status()
