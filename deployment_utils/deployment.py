import os
import logging
import subprocess
from deployment_utils.create_obj import PackerConfig
from deployment_utils.file_handling import create_temp_folder, handle_node_file_structure, remove_temp_folder
from deployment_utils.templating import render_packer_file, render_user_data


def deployment(conf: PackerConfig):
    # initiate logger
    logger = logging.getLogger()

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
            tmp_path = handle_node_file_structure(root_template_path=template_folder_path, folder_path=folder_path, node=node)

            # generate the templates
            render_packer_file(template_folder_path=template_folder_path, tmp_path=tmp_path, config=conf, node=node)
            render_user_data(root_path=template_folder_path, tmp_path=tmp_path, config_obj=conf)

            # now cd to node dir
            os.chdir(tmp_path)

            # packer command
            logger.info(f"Starting {node.node_name} deployment...")
            command = ["packer", "build", fr".\{node.node_name}.pkr.hcl"]
            process = subprocess.Popen(command, shell=True)
            process.wait()
            logger.info(f"Packer Info: {process}")

            # change back to root temp folder
            os.chdir(template_folder_path)
    finally:
        # remove_temp_folder(folder_path=folder_path)
        print("Finally!")

