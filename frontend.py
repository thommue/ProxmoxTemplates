import logging
import streamlit as st
from proxmoxer import ProxmoxAPI
from contextlib import contextmanager
from deployment_utils.deployment import deployment
from deployment_utils.create_obj import PackerConfig, ProxmoxNode
from proxmox_utils.utils import get_local_isos, get_network_bridges


class StreamlitHandler(logging.Handler):
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.log_message = ""

    def emit(self, record):
        message = self.format(record)
        self.log_message += message + "\n"
        self.placeholder.text(self.log_message)

@contextmanager
def streamlit_logger(placeholder):
    handler = StreamlitHandler(placeholder)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    try:
        yield
    finally:
        logger.removeHandler(handler)


# set a title / Header
st.title("Proxmox Template Wizard with Packer 🚀")

# Initialize session state for form submission
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'form2_submitted' not in st.session_state:
    st.session_state.form2_submitted = False
if 'proxmox_url' not in st.session_state:
    st.session_state.proxmox_url = ""
if 'proxmox_user' not in st.session_state:
    st.session_state.proxmox_user = ""
if 'proxmox_api_token_name' not in st.session_state:
    st.session_state.proxmox_api_token_name = ""
if 'proxmox_api_token_secret' not in st.session_state:
    st.session_state.proxmox_api_token_secret = ""
if 'verify_ssl' not in st.session_state:
    st.session_state.verify_ssl = False
if 'proxmox_nodes' not in st.session_state:
    st.session_state.proxmox_nodes = []
if 'local_isos' not in st.session_state:
    st.session_state.local_isos = []
if 'network_bridges' not in st.session_state:
    st.session_state.network_bridges = []


# Define a function to handle form submission
def handle_form_submit() -> None:
    if proxmox_url and proxmox_user and proxmox_api_token_name and proxmox_api_token_secret:
        # Establish a connection to the Proxmox server
        proxmox = ProxmoxAPI(proxmox_url, user=proxmox_user, token_name=proxmox_api_token_name,
                             token_value=proxmox_api_token_secret,
                             verify_ssl=verify_ssl)
        st.session_state.form_submitted = True
        st.session_state.proxmox_url = proxmox_url
        st.session_state.proxmox_user = proxmox_user
        st.session_state.proxmox_api_token_name = proxmox_api_token_name
        st.session_state.proxmox_api_token_secret = proxmox_api_token_secret
        st.session_state.verify_ssl = verify_ssl
        st.session_state.proxmox_nodes = proxmox.nodes.get()
        st.session_state.local_isos = get_local_isos(proxmox)
        st.session_state.network_bridges = get_network_bridges(proxmox)
        st.rerun()
    else:
        st.error("Please fill out all the fields to enable the submit button.")


def check_state(requred_field, optional_ssh_fields) -> PackerConfig:
    if optional_ssh_fields and not (ssh_username and path_to_ssh_key_file and ssh_public_key):
        st.error("If you want the ssh option, please fill out all options!")
    elif not requred_field:
        st.error("Please fill out all the fields to create the template.")
    else:
        packer_conf = PackerConfig(
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
            proxmox_nodes=[ProxmoxNode(node_name=selected_node, vm_id=template_id + i) for i, selected_node in enumerate(selected_nodes)],
            tags=template_tags,
            keyboard_layout=keyboard_layout,
            timezone=timezone,
            tls_verification="true" if st.session_state.verify_ssl else "false",
            additional_packages=[] if "None" in packages else packages
        )
        if optional_ssh_fields:
            packer_conf.ssh_username = ssh_username
            packer_conf.path_to_ssh_key_file = path_to_ssh_key_file
            packer_conf.ssh_public_key = ssh_public_key
        # Simulate a process with intermediate updates
        # progress_text = st.empty()
        # for i in range(10):
        #     progress_text.text(f"Processing step {i + 1}/5...")
        #     time.sleep(1)  # Simulate a step taking time
        return packer_conf


# set up a form, so the user can input the ip of the proxmox node and the token
if not st.session_state.form_submitted:
    with st.form("proxmox_form"):
        st.write("Please setup the connection details for your Proxmox server:")

        proxmox_url = st.text_input("Url:", placeholder="10.10.0.10")

        proxmox_user = st.text_input("User:", placeholder="root@...")

        proxmox_api_token_name = st.text_input("Token Name:", placeholder="YourTokenName")

        proxmox_api_token_secret = st.text_input("Token Secret:", placeholder="xxxxx-xxxx-...")

        verify_ssl = st.checkbox("SSL True")

        submit_button = st.form_submit_button("Set Proxmox Connection")

    # Conditional logic for enabling the form submission
    if submit_button:
        with st.spinner("Establishing the connection to proxmox..."):
            handle_form_submit()

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
            placeholder="Choose nodes..."
        )
        ubuntu_os_version = st.selectbox("Select the ubuntu os version", ["ubuntu-20-04-server", "ubuntu-22-04-server-single", "ubuntu-22-04-server-terraform"], placeholder="ubuntu-20-04, ...")
        template_id = st.number_input("Template VM ID (the id will incrementally increase):", min_value=1, max_value=999, placeholder="900")
        template_name = st.text_input("Template name", placeholder="template-ubuntu-22-04")
        template_description = st.text_input("Template description", placeholder="Ubuntu 22.04 template ....")
        template_tags = st.text_input("Template tags (Please input it, seperated with a comma)", placeholder="template, ubuntu, ...")
        template_iso = st.selectbox("Select a ISO (must be available on all selected nodes!)", st.session_state.local_isos, index=None, placeholder="Select ISO...")
        storage_pool = st.text_input("Your storage pool:", placeholder="hapool01...")

        col1, col2 = st.columns(2)

        with col1:
            disk_size = st.number_input("choose disk size in G:", min_value=1,
                                          max_value=999, placeholder="32")
            cores = st.number_input("choose the core size:", min_value=1,
                                          max_value=999, placeholder="4")
            keyboard_layout = st.text_input("Keyboard layout", placeholder="de")

        with col2:
            memory = st.number_input("choose the memory size (MB):", min_value=1,
                                          max_value=100000, placeholder="4092")
            bridge = st.selectbox("Select a Bridge (must be available on all nodes!)", st.session_state.network_bridges, index=None, placeholder="Select bridge...")
            timezone = st.text_input("Timezone", placeholder="Europe/Vienna")

        st.markdown("##### Optional settings for ssh access (can be leave blank if not needed):")

        ssh_username = st.text_input("SSH Username", placeholder="TestSSH")
        path_to_ssh_key_file = st.text_input("Path to your local ssh key file", placeholder="~/.ssh/homelab")
        ssh_public_key = st.text_input("Your public ssh key", placeholder="ssh-rsa xxxxxx")

        packages = st.multiselect(label="Preinstall on template: ", options=["None", "docker & docker-compose"],
                                  default=["None"] ,placeholder="Select what you want...")

        # Check if all required fields are filled
        all_required_fields_filled = selected_nodes and template_id and template_name and template_description and template_tags and template_iso and disk_size and cores and keyboard_layout and memory and bridge and timezone

        # Check if optional fields are filled
        all_shh_fields = ssh_username or path_to_ssh_key_file or ssh_public_key

        template_submit = st.form_submit_button("Create Template(s)")

    if template_submit:
        placeholder = st.empty()
        with placeholder:
            with st.spinner("Packer Deployment in progress..."):
                with streamlit_logger(placeholder):
                    conf = check_state(all_required_fields_filled, all_shh_fields)
                    deployment(conf=conf)
                    st.success("Template was successfully created!")

