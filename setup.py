from setuptools import find_packages, setup

PACKAGE_NAME = "ciscosupportapi"

INSTALLATION_REQUIREMENTS = [
    "requests>=2.25.1",
]

setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    packages=find_packages(include=[PACKAGE_NAME, PACKAGE_NAME + ".*"]),
    install_requires=INSTALLATION_REQUIREMENTS,
)
