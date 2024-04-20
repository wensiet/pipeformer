from pydantic import BaseModel


class ComputeConfig(BaseModel):
    name: str
    os: str
    preset: str
    ssh_key: str

    custom_scripts: list
