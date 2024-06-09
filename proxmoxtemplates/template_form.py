import streamlit as st
from proxmoxtemplates.frontend_utils.utils import setup_logger
from proxmoxtemplates.deployment_utils.deployment import deployment
from proxmoxtemplates.deployment_utils.create_obj import (
    PackerConfig,
    ProxmoxNode,
)


def template_form() -> None:
    with st.form(key="template_setup"):
        st.markdown("#### Setup of the template:")

        selected_nodes = st.multiselect(
            "One which node, should the template be placed?",
            st.session_state.my_proxmox.proxmox_nodes,
            placeholder="Choose nodes...",
        )
        ubuntu_os_version = st.selectbox(
            "Select the ubuntu os version",
            [
                "ubuntu-20-04-server",
                "ubuntu-22-04-server",
                "ubuntu-22-04-server-terraform",
                "ubuntu-24-04-server",
            ],
            placeholder="ubuntu-20-04, ...",
        )
        template_id = st.number_input(
            "Template VM ID (the id will incrementally increase):",
            min_value=1,
            max_value=999,
            placeholder="900",
        )
        template_name = st.text_input(
            "Template name", placeholder="template-ubuntu-22-04"
        )
        template_description = st.text_input(
            "Template description", placeholder="Ubuntu 22.04 template ...."
        )
        template_tags = st.text_input(
            "Template tags (Please input it, seperated with a comma)",
            placeholder="template, ubuntu, ...",
        )
        template_iso = st.selectbox(
            "Select a ISO (must be available on all selected nodes!)",
            st.session_state.my_proxmox.local_isos,
            index=None,
            placeholder="Select ISO...",
        )
        storage_pool = st.selectbox(
            "Select a storage pool.",
            st.session_state.my_proxmox.storage_pools,
            index=None,
            placeholder="Select a storage pool...",
        )

        col1, col2 = st.columns(2)

        with col1:
            disk_size = st.number_input(
                "choose disk size in G:",
                min_value=1,
                max_value=999,
                placeholder="32",
            )
            cores = st.number_input(
                "choose the core size:", min_value=1, max_value=999, placeholder="4"
            )
            keyboard_layout = st.text_input("Keyboard layout", placeholder="de")

        with col2:
            memory = st.number_input(
                "choose the memory size (MB):",
                min_value=1024,
                max_value=100000,
                placeholder="4092",
            )
            bridge = st.selectbox(
                "Select a Bridge (must be available on all nodes!)",
                st.session_state.my_proxmox.network_bridges,
                index=None,
                placeholder="Select bridge...",
            )
            timezone = st.text_input("Timezone", placeholder="Europe/Vienna")

        st.markdown(
            "##### Settings for ssh access (is needed for the packer connection):"
        )

        ssh_username = st.text_input("SSH Username", placeholder="TestSSH")
        path_to_ssh_key_file = st.text_input(
            "Path to your local ssh key file", placeholder="~/.ssh/homelab"
        )
        ssh_public_key = st.text_input(
            "Your public ssh key", placeholder="ssh-rsa xxxxxx"
        )

        packages = st.multiselect(
            label="Preinstall on template: ",
            options=["None", "docker & docker-compose"],
            default=["None"],
            placeholder="Select what you want...",
        )

        # Check if all required fields are filled
        required_fields = [
            selected_nodes,
            template_id,
            template_name,
            template_description,
            template_tags,
            disk_size,
            cores,
            keyboard_layout,
            memory,
            timezone,
            ssh_username,
            path_to_ssh_key_file,
            ssh_public_key,
        ]
        all_required_fields_filled = all(required_fields)

        template_submit = st.form_submit_button("Create Template(s)")

        if (
            template_submit
            and all_required_fields_filled
            and ubuntu_os_version
            and template_iso
            and storage_pool
            and bridge
        ):
            placeholder_for_logger = st.empty()
            logger, log_stream = setup_logger()
            with st.spinner("Packer Deployment in progress..."):
                deployment(
                    conf=PackerConfig(
                        ubuntu_version=ubuntu_os_version,
                        proxmox_api_url=f"https://{st.session_state.my_proxmox.proxmox_url}:8006/api2/json",
                        proxmox_api_token_id=f"{st.session_state.my_proxmox.proxmox_user}!{st.session_state.my_proxmox.proxmox_api_token_name}",
                        proxmox_api_token_secret=st.session_state.my_proxmox.proxmox_api_token_secret,
                        template_name=template_name,
                        template_description=template_description,
                        iso_file=template_iso,
                        iso_storage_pool="local",
                        disk_size=f"{disk_size}G",
                        storage_pool=storage_pool,
                        storage_pool_type="rbd",
                        cores=f"{cores}",
                        memory=f"{memory}",
                        network_bridge=bridge,
                        packer_bind_address=st.session_state.my_proxmox.local_ip,
                        ssh_username=ssh_username,
                        path_to_ssh_key_file=path_to_ssh_key_file,
                        ssh_public_key=ssh_public_key,
                        proxmox_nodes=[
                            ProxmoxNode(
                                node_name=selected_node, vm_id=int(template_id + i)
                            )
                            for i, selected_node in enumerate(selected_nodes)
                        ],
                        tags=template_tags,
                        keyboard_layout=keyboard_layout,
                        timezone=timezone,
                        tls_verification=(
                            "true"
                            if st.session_state.my_proxmox.verify_ssl
                            else "false"
                        ),
                        additional_packages=[] if "None" in packages else packages,
                    ),
                    logger=logger,
                    placeholder=placeholder_for_logger,
                    log_stream=log_stream,
                )
                st.success("Template was successfully created!")
        else:
            st.error("Please fill out all the fields to enable the submit button.")
