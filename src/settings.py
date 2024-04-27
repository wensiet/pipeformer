import os


class ProvisionerSettings:
    host: str = "https://api.timeweb.cloud/api"
    token: str = os.environ.get("TIMEWEB_API_TOKEN")


class AppSettings:
    service_key_id: int = 178611
    sentry_dsn: str = ("https://glet_a6255ea99a8f3cda886bf26f323331b8"
                       "@observe.gitlab.com:443/errortracking/api/v1/projects/56957331")
    service_key: str = ("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPhq"
                        "/C7s6A07iJ8LGowgFCYujAtL+vF/Yhp95hnaV2oJ wensietyt@gmail.com")
