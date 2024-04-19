import os


class ProvisionerSettings:
    host: str = "https://api.timeweb.cloud/api"
    token: str = os.environ.get("TIMEWEB_API_TOKEN")
