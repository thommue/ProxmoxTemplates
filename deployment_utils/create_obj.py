from typing import List, Optional
from pydantic import BaseModel


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
    ssh_username: Optional[str] = None
    path_to_ssh_key_file: Optional[str] = None
    ssh_public_key: Optional[str] = None
    proxmox_nodes: List[ProxmoxNode]
    tags: str
    keyboard_layout: str
    timezone: str
    tls_verification: str
    additional_packages: list[str]
