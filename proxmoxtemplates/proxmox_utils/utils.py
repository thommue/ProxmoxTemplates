def get_local_isos_and_storage(proxmox) -> tuple[list[str], list[str]]:
    iso_list = []
    proxmox_storage = []
    for node in proxmox.nodes.get():
        storage_list = proxmox.nodes(node["node"]).storage.get()
        for storage in storage_list:
            if storage["storage"] == "local":
                iso_content = (
                    proxmox.nodes(node["node"])
                    .storage(storage["storage"])
                    .content.get()
                )
                for content in iso_content:
                    if content["volid"] not in iso_list:
                        iso_list.append(content["volid"])
            else:
                if storage["storage"] not in proxmox_storage:
                    proxmox_storage.append(storage["storage"])
    return iso_list, proxmox_storage


def get_network_bridges(proxmox) -> list[str]:
    bridge_list = []
    for node in proxmox.nodes.get():
        network_list = proxmox.nodes(node["node"]).network.get()
        for network in network_list:
            if network["type"] == "bridge":
                if network["iface"] not in bridge_list:
                    bridge_list.append(network["iface"])
    return bridge_list
