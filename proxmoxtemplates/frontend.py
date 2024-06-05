import streamlit as st
from proxmoxer import ProxmoxAPI  # type: ignore
from .deployment_utils.deployment import deployment
from .deployment_utils.create_obj import PackerConfig, ProxmoxNode
from .frontend_utils.utils import setup_logger
from .proxmox_utils.utils import get_local_isos_and_storage, get_network_bridges


# Define a function to handle form submission
def handle_form_submit(
    proxmox_url: str,
    proxmox_user: str,
    proxmox_api_token_name: str,
    proxmox_api_token_secret: str,
    verify_ssl: bool,
) -> None:
    # Establish a connection to the Proxmox server
    proxmox = ProxmoxAPI(
        proxmox_url,
        user=proxmox_user,
        token_name=proxmox_api_token_name,
        token_value=proxmox_api_token_secret,
        verify_ssl=verify_ssl,
    )
    st.session_state.form_submitted = True
    st.session_state.proxmox_url = proxmox_url
    st.session_state.proxmox_user = proxmox_user
    st.session_state.proxmox_api_token_name = proxmox_api_token_name
    st.session_state.proxmox_api_token_secret = proxmox_api_token_secret
    st.session_state.verify_ssl = verify_ssl
    st.session_state.proxmox_nodes = proxmox.nodes.get()
    st.session_state.local_isos, st.session_state.storage_pools = (
        get_local_isos_and_storage(proxmox)
    )
    st.session_state.network_bridges = get_network_bridges(proxmox)
    st.rerun()


def main():
    # set a title / Header
    st.title("Proxmox Template Wizard with Packer 🚀")

    # Initialize session state for form submission
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "form2_submitted" not in st.session_state:
        st.session_state.form2_submitted = False
    if "proxmox_url" not in st.session_state:
        st.session_state.proxmox_url = ""
    if "proxmox_user" not in st.session_state:
        st.session_state.proxmox_user = ""
    if "proxmox_api_token_name" not in st.session_state:
        st.session_state.proxmox_api_token_name = ""
    if "proxmox_api_token_secret" not in st.session_state:
        st.session_state.proxmox_api_token_secret = ""
    if "verify_ssl" not in st.session_state:
        st.session_state.verify_ssl = False
    if "proxmox_nodes" not in st.session_state:
        st.session_state.proxmox_nodes = []
    if "local_isos" not in st.session_state:
        st.session_state.local_isos = []
    if "network_bridges" not in st.session_state:
        st.session_state.network_bridges = []

    # set up a form, so the user can input the ip of the proxmox node and the token
    if not st.session_state.form_submitted:
        with st.form("proxmox_form"):
            st.write("Please setup the connection details for your Proxmox server:")

            proxmox_url = st.text_input("Url:", placeholder="10.10.0.10")

            proxmox_user = st.text_input("User:", placeholder="root@...")

            proxmox_api_token_name = st.text_input(
                "Token Name:", placeholder="YourTokenName"
            )

            proxmox_api_token_secret = st.text_input(
                "Token Secret:", placeholder="xxxxx-xxxx-..."
            )

            verify_ssl = st.checkbox("SSL True")

            submit_button = st.form_submit_button("Set Proxmox Connection")

        # Conditional logic for enabling the form submission
        if submit_button and all(
            [
                proxmox_url,
                proxmox_user,
                proxmox_api_token_name,
                proxmox_api_token_secret,
                verify_ssl,
            ]
        ):
            with st.spinner("Establishing the connection to proxmox..."):
                handle_form_submit(
                    proxmox_url=proxmox_url,
                    proxmox_user=proxmox_user,
                    proxmox_api_token_name=proxmox_api_token_name,
                    proxmox_api_token_secret=proxmox_api_token_secret,
                    verify_ssl=verify_ssl,
                )
        else:
            st.error("Please fill out all the fields to enable the submit button.")

    if st.session_state.form_submitted and not st.session_state.form2_submitted:
        st.success("Proxmox connection setup complete!")
        with st.form("template_setup"):
            st.markdown("#### Setup of the template:")

            if len(st.session_state.proxmox_nodes) >= 1:
                node_choices = []
                for node in st.session_state.proxmox_nodes:
                    node_choices.append(node["node"])
            else:
                st.error("No nodes!")

            selected_nodes = st.multiselect(
                "One which node, should the template be placed?",
                node_choices,
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
                st.session_state.local_isos,
                index=None,
                placeholder="Select ISO...",
            )
            storage_pool = st.selectbox(
                "Select a storage pool.",
                st.session_state.storage_pools,
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
                    st.session_state.network_bridges,
                    index=None,
                    placeholder="Select bridge...",
                )
                timezone = st.text_input("Timezone", placeholder="Europe/Vienna")

            st.markdown(
                "##### Optional settings for ssh access (can be leave blank if not needed):"
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
                template_iso,
                disk_size,
                cores,
                keyboard_layout,
                memory,
                bridge,
                timezone,
                ssh_username,
                path_to_ssh_key_file,
                ssh_public_key,
            ]
            all_required_fields_filled = all(required_fields)

            template_submit = st.form_submit_button("Create Template(s)")

        if template_submit and all_required_fields_filled:
            placeholder_for_logger = st.empty()
            logger, log_stream = setup_logger()
            with st.spinner("Packer Deployment in progress..."):
                deployment(
                    conf=PackerConfig(
                        ubuntu_version=ubuntu_os_version,
                        proxmox_api_url=f"https://{st.session_state.proxmox_url}:8006/api2/json",
                        proxmox_api_token_id=f"{st.session_state.proxmox_user}!{st.session_state.proxmox_api_token_name}",
                        proxmox_api_token_secret=st.session_state.proxmox_api_token_secret,
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
                        packer_bind_address="192.168.1.56",
                        ssh_username=ssh_username,
                        path_to_ssh_key_file=path_to_ssh_key_file,
                        ssh_public_key=ssh_public_key,
                        proxmox_nodes=[
                            ProxmoxNode(node_name=selected_node, vm_id=template_id + i)
                            for i, selected_node in enumerate(selected_nodes)
                        ],
                        tags=template_tags,
                        keyboard_layout=keyboard_layout,
                        timezone=timezone,
                        tls_verification=(
                            "true" if st.session_state.verify_ssl else "false"
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


if __name__ == "__main__":
    main()
