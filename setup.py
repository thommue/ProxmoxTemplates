from setuptools import setup, find_packages


setup(
    name="proxmoxtemplates",
    version="0.1",
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
    package_data={"proxmoxtemplates": ["deployment_utils/deployment_template/*"]},
    include_package_data=True,
)
