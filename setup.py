from setuptools import setup, find_packages


def read_requirements() -> list[str]:
    with open("requirements.txt", "r") as req:
        lines = req.readline()
    return [line.strip() for line in lines if line and not line.startswith("#")]


setup(
    name="proxmoxtemplates",
    version="0.1",
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "proxmoxtemplates_app=proxmoxtemplates.app:main",
        ],
    },
)
