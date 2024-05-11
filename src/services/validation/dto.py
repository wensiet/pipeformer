import re
import httpx
import yaml
import logging

from pydantic import BaseModel, HttpUrl, field_validator
from typing import List, Any

valid_systems = (
    'archlinux_2_12', 'debian_10', 'debian_11', 'debian_12',
    'ubuntu_18_04', 'ubuntu_20_04', 'ubuntu_22_04',
    'centos_7', 'centos_8', 'centos_9'
)
valid_regions = ('SPB-1', 'MSK-1')
valid_configurations = (
    (1, '1GB', '15GB'),
    (1, '2GB', '30GB'),
    (2, '2GB', '40GB'),
    (2, '4GB', '50GB'),
    (4, '8GB', '80GB')
)


class Flavor(BaseModel):
    operating_system: str
    disk_space: str
    cpu_cores: int
    RAM: str
    region: str

    @field_validator('operating_system')
    @classmethod
    def validate_operating_system(cls, value):
        logging.info("Validating operating_system")
        if value not in valid_systems:
            logging.error("Invalid operating system")
            raise ValueError()
        return value

    @field_validator('region')
    @classmethod
    def validate_region(cls, value):
        logging.info("Validating region")
        if value not in valid_regions:
            logging.error("Invalid region")
            raise ValueError()
        return value


class Var(BaseModel):
    name: str
    value: Any

    @field_validator('name')
    @classmethod
    def validate_var_name(cls, value):
        logging.info("Validating name")
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', value):
            logging.error("Invalid variable name.")
            raise ValueError()
        return value


class Playbook(BaseModel):
    name: str
    link: HttpUrl
    vars: List[Var] = []

    @field_validator('link')
    @classmethod
    def validate_link(cls, value):
        logging.info("Validating link")
        client = httpx.Client()
        address = str(value)
        response = client.request(
            "GET",
            address,
        )
        if response.status_code != 200:
            logging.error("Link does not work")
            raise ValueError()
        data = response.text
        try:
            yaml.safe_load(data)
        except yaml.YAMLError:
            logging.error("Link leads to an invalid yaml file")
            raise ValueError()
        return value


class ComputeConfig(BaseModel):
    ssh: str
    flavor: Flavor
    playbooks: List[Playbook] = []

    @field_validator('ssh')
    @classmethod
    def validate_ssh(cls, value):
        logging.info("Validating ssh")
        if not re.match(r'^ssh-(?:\w+ )?(?:[A-Za-z0-9+/]+={0,3}\s?)+(?: .+)?$', value):
            logging.error("Invalid ssh key")
            raise ValueError()
        return value

    @field_validator('flavor')
    @classmethod
    def validate_flavor(cls, value):
        logging.info("Validating flavor")
        if (value.cpu_cores, value.RAM, value.disk_space) not in valid_configurations:
            logging.error("Invalid flavor configuration")
            raise ValueError()
        return value
