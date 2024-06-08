import os
import subprocess
import time
from io import StringIO
from logging import Logger
from streamlit.delta_generator import DeltaGenerator
from .create_obj import PackerConfig
from .file_handling import (
    create_temp_folder,
    handle_node_file_structure,
    remove_temp_folder,
)
from .templating import (
    render_packer_file,
    render_user_data,
)


def deployment(
    conf: PackerConfig,
    logger: Logger,
    placeholder: DeltaGenerator,
    log_stream: StringIO,
) -> None:
    # get the root path of this file
    root_path = os.path.dirname(os.path.abspath(__file__))

    # change to the template folder
    template_folder_path = os.path.join(root_path, "deployment_template")

    # generate a temp folder
    folder_path = create_temp_folder(template_folder_path=template_folder_path)

    try:
        # the template file need to be generated per each node
        for node in conf.proxmox_nodes:
            # log
            logger.info("_________________________")
            logger.info(f"Starting {node.node_name} templating...")
            placeholder.text(log_stream.getvalue())
            tmp_path = handle_node_file_structure(
                root_template_path=template_folder_path,
                folder_path=folder_path,
                node=node,
            )

            # generate the templates
            render_packer_file(
                template_folder_path=template_folder_path,
                tmp_path=tmp_path,
                config=conf,
                node=node,
            )
            render_user_data(
                root_path=template_folder_path, tmp_path=tmp_path, config_obj=conf
            )

            # now cd to node dir
            os.chdir(tmp_path)

            # packer command
            logger.info(f"Starting {node.node_name} deployment...")
            placeholder.text(log_stream.getvalue())
            command = ["packer", "build", rf".\{node.node_name}.pkr.hcl"]
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            while process.stdout.readline() != "" and process.poll() is None:  # type: ignore
                logger.info(f"{process.stdout.readline()}")  # type: ignore
                placeholder.text(log_stream.getvalue())

            # change back to root temp folder
            os.chdir(template_folder_path)
    finally:
        time.sleep(1)
        remove_temp_folder(folder_path=folder_path)
