import pathlib

import pkg_resources
from setuptools import Extension, find_packages, setup

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
            "device",
            sources=["EnumerateDevice/EnumerateDevice/device.cpp"],
        )
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
)

setup(**setup_args)
