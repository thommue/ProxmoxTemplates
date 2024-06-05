import os
from jinja2 import Environment, FileSystemLoader
from .create_obj import PackerConfig, ProxmoxNode


def render_packer_file(
    template_folder_path: str, tmp_path: str, config: PackerConfig, node: ProxmoxNode
) -> None:
    # render
    template = Environment(
        loader=FileSystemLoader(os.path.join(template_folder_path, "jinja_templates"))
    ).get_template("base_template.pkr.hcl.j2")
    rendered_content = template.render(config=config, node=node)

    # save
    with open(
        (os.path.join(tmp_path, f"{node.node_name}.pkr.hcl")), "w"
    ) as packer_file:
        packer_file.write(rendered_content)


def render_user_data(root_path: str, tmp_path: str, config_obj: PackerConfig) -> None:
    # render
    template = Environment(
        loader=FileSystemLoader(os.path.join(root_path, "jinja_templates"))
    ).get_template("user-data.j2")
    rendered_content = template.render(config=config_obj)

    # save
    with open((os.path.join(tmp_path, "http", "user-data")), "w") as user_file:
        user_file.write(rendered_content)
