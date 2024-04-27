from enum import StrEnum
from typing import Optional, List

from pydantic import BaseModel


class VPSConfiguration(BaseModel):
    configuration_id: int = None
    disk: int
    cpu: int
    ram: int


class VPSNetwork(BaseModel):
    id: str
    floating_ip: Optional[str]


class CreateServerRequest(BaseModel):
    configuration: Optional[VPSConfiguration] = None
    is_ddos_guard: bool
    os_id: Optional[int] = None
    image_id: Optional[int] = None
    software_id: Optional[int] = None
    preset_id: Optional[int] = None
    bandwidth: int
    name: str
    avatar_id: Optional[str] = None
    comment: Optional[str] = None
    ssh_keys_ids: Optional[list[int]] = None
    network: Optional[VPSNetwork] = None
    cloud_init: Optional[str] = None
    availability_zone: Optional[str] = None


class Preset:
    c1r1d15 = 2447
    c1r2d30 = 2449
    c2r2d40 = 2451
    c2r4d50 = 2453
    c4r8d80 = 2455

    @classmethod
    def get_preset(cls, preset: str) -> int:
        preset_cls = getattr(cls, preset)
        if not preset_cls:
            raise ValueError(f"Invalid preset: {preset}")
        return preset_cls


class OS:
    centos_7 = 39
    centos_8 = 73
    ubuntu_18_04 = 47
    ubuntu_20_04 = 61
    ubuntu_22_04 = 79
    debian_10 = 57
    debian_11 = 67

    @classmethod
    def get_os(cls, os: str) -> int:
        os_cls = getattr(cls, os)
        if not os_cls:
            raise ValueError(f"Invalid OS: {os}")
        return os_cls


class IP(BaseModel):
    ip: str
    is_main: bool
    ptr: Optional[str]
    type: str


class Network(BaseModel):
    type: str
    bandwidth: int
    ips: List[IP]
    blocked_ports: Optional[List[int]]


class Disk(BaseModel):
    size: int
    used: int
    id: int
    type: str
    is_mounted: bool
    is_system: bool
    status: str
    system_name: str
    is_auto_backup: bool


class OSResponse(BaseModel):
    id: int
    name: str
    version: str


class Compute(BaseModel):
    id: int
    name: str
    comment: str
    os: OSResponse
    software: Optional[dict]
    preset_id: int
    configurator_id: Optional[int]
    location: str
    availability_zone: str
    boot_mode: str
    status: str
    start_at: Optional[str]
    is_ddos_guard: bool
    is_master_ssh: bool
    avatar_id: Optional[str]
    vnc_pass: str
    cpu: int
    cpu_frequency: str
    ram: int
    created_at: str
    networks: List[Network]
    disks: List[Disk]
    image: Optional[dict]
    root_pass: Optional[str]
    cloud_init: Optional[str]
    is_qemu_agent: bool

    def extract_ipv4(self):
        for network in self.networks:
            for ip in network.ips:
                if ip.type == "ipv4":
                    return ip
        raise ValueError("No IPv4 found")
