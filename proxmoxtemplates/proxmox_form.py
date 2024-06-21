import streamlit as st
from proxmoxer import ProxmoxAPI  # type: ignore
from proxmoxtemplates.deployment_utils.create_obj import MyProxmox
from proxmoxtemplates.proxmox_utils.utils import (
    get_local_isos_and_storage,
    get_network_bridges,
)


def handle_form_submit(my_proxmox: MyProxmox) -> MyProxmox:
    # Establish a connection to the Proxmox server
    proxmox = ProxmoxAPI(
        my_proxmox.proxmox_url,
        user=my_proxmox.proxmox_user,
        token_name=my_proxmox.proxmox_api_token_name,
        token_value=my_proxmox.proxmox_api_token_secret,
        verify_ssl=my_proxmox.verify_ssl,
        timeout=20,
    )
    my_proxmox.proxmox_nodes = [node["node"] for node in proxmox.nodes.get()]
    my_proxmox.local_isos, my_proxmox.storage_pools = get_local_isos_and_storage(
        proxmox
    )
    my_proxmox.network_bridges = get_network_bridges(proxmox)
    return my_proxmox


def proxmox_form() -> None:
    with st.form(key="proxmox_form"):
        st.write("Please setup the connection details for your Proxmox server:")

        proxmox_url = st.text_input("Url:", placeholder="10.10.0.10")

        proxmox_user = st.text_input("User:", placeholder="root@...")

        proxmox_api_token_name = st.text_input(
            "Token Name:", placeholder="YourTokenName"
        )

        proxmox_api_token_secret = st.text_input(
            "Token Secret:", placeholder="xxxxx-xxxx-..."
        )

        local_ip = st.text_input(
            "Your local IP to establish the connection:", placeholder="10.10.10.10"
        )

        verify_ssl = st.checkbox("SSL True", value=False)

        submit_button = st.form_submit_button("Set Proxmox Connection")

        # Conditional logic for enabling the form submission
        if submit_button and all(
            [
                proxmox_url,
                proxmox_user,
                proxmox_api_token_name,
                proxmox_api_token_secret,
                verify_ssl,
                local_ip,
            ]
        ):
            with st.spinner("Establishing the connection to proxmox..."):
                my_proxmox = handle_form_submit(
                    my_proxmox=MyProxmox(
                        proxmox_url=proxmox_url,
                        proxmox_user=proxmox_user,
                        proxmox_api_token_name=proxmox_api_token_name,
                        proxmox_api_token_secret=proxmox_api_token_secret,
                        verify_ssl=verify_ssl,
                        local_ip=local_ip,
                    )
                )
                st.session_state.my_proxmox = my_proxmox
                st.session_state.form_submitted = True
                st.rerun()
        else:
            st.error("Please fill out all the fields to enable the submit button.")
