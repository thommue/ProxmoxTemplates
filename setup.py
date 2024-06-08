import os
from setuptools import setup, find_packages

version_string = os.environ.get("PACKAGE_VERSION", "0.0.0.dev0")

setup(
    name="proxmoxtemplates",
    version=str(version_string),
    packages=find_packages(),
    install_requires=[
        "streamlit==1.34.0",
        "proxmoxer==2.0.1",
        "pydantic==2.7.1",
        "jinja2==3.1.4",
        "keyboard==0.13.5",
    ],
    entry_points={
        "console_scripts": [
            "proxmoxtemplates_app=bin.run_app:main",
        ],
    },
    include_package_data=True,
)
