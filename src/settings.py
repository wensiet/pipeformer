import os


class ProvisionerSettings:
    host: str = "https://api.timeweb.cloud/api"
    token: str = os.environ.get("TIMEWEB_API_TOKEN")


class GrafanaSettings:
    host: str = os.getenv("GRAFANA_HOST", "https://grafana.levelware.ru").rstrip("/")
    folder_uid: str = os.getenv("GRAFANA_FOLDER_UID", "ddkp8uqcg5slcf")
    base_dashboard: str = os.getenv("GRAFANA_BASE_DASHBOARD", "zabbix-vmware-esxi")
    zabbix_group: str = os.getenv("GRAFANA_ZABBIX_GROUP", "Linux servers")


class AppSettings:
    service_key_id: int = 178611
    sentry_dsn: str = ("https://glet_a6255ea99a8f3cda886bf26f323331b8"
                       "@observe.gitlab.com:443/errortracking/api/v1/projects/56957331")
    service_key: str = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBhC2d1n+G8MgiscLGY7DGGe0fASTiwCBApG2z1xYT6r service"
