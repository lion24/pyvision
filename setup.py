"""Setup script for the package."""

import pathlib

import pkg_resources
from setuptools import Extension, setup

setup_dir = pathlib.Path(__file__).parent.resolve()

requirements_path = setup_dir / "requirements.txt"
with requirements_path.open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]

setup_args = dict(
    install_requires=install_requires,
    ext_modules=[
        Extension(
            "pyvision.device",
            sources=["./src/pyvision/device_ext/device.cpp"],
        )
    ],
)

setup(**setup_args)  # type: ignore
