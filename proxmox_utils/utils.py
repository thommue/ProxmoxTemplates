def get_local_isos(proxmox):
    iso_list = []
    for node in proxmox.nodes.get():
        storage_list = proxmox.nodes(node['node']).storage.get()
        # print("The storage content:")
        # print(storage_list)
        for storage in storage_list:
            if storage['storage'] == 'local':
                iso_content = proxmox.nodes(node['node']).storage(storage['storage']).content.get()
                # print(iso_content)
                for content in iso_content:
                    if content['volid'] not in iso_list:
                        iso_list.append(content['volid'])
    return iso_list


def get_network_bridges(proxmox):
    bridge_list = []
    for node in proxmox.nodes.get():
        network_list = proxmox.nodes(node['node']).network.get()
        for network in network_list:
            if network['type'] == 'bridge':
                if network["iface"] not in bridge_list:
                    bridge_list.append(network["iface"])
    return bridge_list
