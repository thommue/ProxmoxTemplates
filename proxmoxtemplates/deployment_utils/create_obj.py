from pydantic import BaseModel
from typing import List, Optional


class MyProxmox(BaseModel):
    proxmox_url: str
    proxmox_user: str
    proxmox_api_token_name: str
    proxmox_api_token_secret: str
    verify_ssl: bool
    local_ip: str
    proxmox_nodes: Optional[list[str]] = None
    local_isos: Optional[list[str]] = None
    storage_pools: Optional[list[str]] = None
    network_bridges: Optional[list[str]] = None


class ProxmoxNode(BaseModel):
    node_name: str
    vm_id: int


class PackerConfig(BaseModel):
    ubuntu_version: str
    proxmox_api_url: str
    proxmox_api_token_id: str
    proxmox_api_token_secret: str
    template_name: str
    template_description: str
    iso_file: str
    iso_storage_pool: str
    disk_size: str
    storage_pool: str
    storage_pool_type: str
    cores: str
    memory: str
    network_bridge: str
    packer_bind_address: str
    ssh_username: str
    path_to_ssh_key_file: str
    ssh_public_key: str
    proxmox_nodes: List[ProxmoxNode]
    tags: str
    keyboard_layout: str
    timezone: str
    tls_verification: str
    additional_packages: list[str]
