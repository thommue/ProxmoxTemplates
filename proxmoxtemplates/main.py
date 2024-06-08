import streamlit as st
from proxmoxtemplates.proxmox_form import proxmox_form
from proxmoxtemplates.template_form import template_form


def initialize_session_state() -> None:
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "form2_submitted" not in st.session_state:
        st.session_state.form2_submitted = False
    if "my_proxmox" not in st.session_state:
        st.session_state.my_proxmox = None


def main() -> None:
    initialize_session_state()
    st.title("Proxmox Template Wizard with Packer 🚀")
    if not st.session_state.form_submitted:
        proxmox_form()

    if st.session_state.form_submitted and not st.session_state.form2_submitted:
        st.success("Proxmox connection setup complete!")
        template_form()


if __name__ == "__main__":
    main()
