from pydantic import BaseModel, HttpUrl
from typing import List


class Flavor(BaseModel):
    operating_system: str
    disk_space: str
    cpu_cores: int
    RAM: str
    region: str


class Var(BaseModel):
    name: str
    value: str


class Playbook(BaseModel):
    name: str
    link: HttpUrl
    vars: List[Var] = []


class ComputeConfig(BaseModel):
    ssh: str
    flavor: Flavor
    playbooks: List[Playbook] = []
