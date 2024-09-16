"""Setup script for the package."""

import os

os.environ["VSLANG"] = "1033"

import pathlib

import tomli
from packaging.requirements import Requirement
from setuptools import Extension, setup  # type: ignore

setup_dir = pathlib.Path(__file__).parent.resolve()

pyproject_toml = setup_dir / "pyproject.toml"
with open(pyproject_toml, "rb") as f:
    tomli_dict = tomli.load(f)
    dependencies = tomli_dict["project"]["dependencies"]

    install_requires = [str(Requirement(line.strip())) for line in dependencies]

setup_args = dict(
    install_requires=install_requires,
    ext_modules=[
        Extension(
            "pyvision.device",
            sources=["./src/pyvision/device_ext/device.cpp"],
            libraries=["Ole32", "OleAut32"],
        )
    ],
)

setup(**setup_args)  # type: ignore
