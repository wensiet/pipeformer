from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class Flavor(BaseModel):
    operating_system: str
    disk_space: str
    cpu_cores: int
    RAM: str
    region: str


class Playbook(BaseModel):
    name: str
    link: HttpUrl
    vars: List[str]


class ComputeConfig(BaseModel):
    ssh: str
    flavor: Flavor
    playbooks: Optional[List[Playbook]] = []
