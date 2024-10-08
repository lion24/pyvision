"""Setup script for the package."""

import os
import sys

os.environ["VSLANG"] = "1033"

import pathlib
import platform
import subprocess
from pprint import pprint
from typing import Any, List

import tomli
from packaging.requirements import Requirement
from setuptools import Extension, setup  # type: ignore
from setuptools.command.build_ext import build_ext  # type: ignore

c_module_name = "pyvision.device"

# Command ilne flags forwarded to CMake (for debug purpose)
cmake_cmd_args: List[str] = []
for f in sys.argv:
    if f.startswith("-D"):
        cmake_cmd_args.append(f)

for f in cmake_cmd_args:
    sys.argv.remove(f)


def _get_env_variable(key: str, default: str = "OFF"):
    if key not in os.environ.keys():
        return default
    return os.environ[key]


def get_version() -> str:
    """Get the version of the package."""
    with open("src/pyvision/__init__.py") as f:
        version = "undefined"
        for line in f:
            if line.startswith("__version__"):
                version = line.strip().split()[-1][1:-1]
    return version


class CMakeExtension(Extension):
    """Extension class for CMake-based extensions."""

    def __init__(
        self,
        name: str,
        cmake_lists_dir: str = ".",
        sources: List[str] = [],
        **kwargs: Any,
    ):
        """Initialize the CMakeExtension.

        Args:
            name (str): The name of the extension.
            cmake_lists_dir (str, optional): The directory containing the CMakeLists.txt file. Defaults to ".".
            sources (List[str], optional): The list of source files for the extension. Defaults to [].
            **kwargs (Any): Additional keyword arguments.
        """
        Extension.__init__(self, name, sources=sources, **kwargs)
        self.cmake_lists_dir = os.path.abspath(cmake_lists_dir)


class CMakeBuild(build_ext):
    """Build extension using CMake."""

    def run(self):
        """Run the build extension process."""
        # Ensure that CMake is installed
        try:
            subprocess.check_call(["cmake", "--version"])
        except OSError:
            raise RuntimeError("CMake must be installed to build the extension")

        # Call the parent class run method to initialize the compiler and other configurations
        super().run()

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext: CMakeExtension):
        """Build the extension.

        Args:
            ext (CMakeExtension): The extension to build.
        """
        extdir = pathlib.Path(self.get_ext_fullpath(ext.name)).parent.resolve()
        cfg = "Debug" if _get_env_variable("PYVISION_DEBUG") == "ON" else "Release"

        # Generate the full module name
        # Python expect that the module name generated by CMake to match the following:
        # <module_name>.<abi>-<platform>.<ext>
        # where <abi> is the python ABI (e.g. cp39) and <platform> is the platform (e.g. win_amd64)
        # and <ext> is the extension (e.g. pyd)
        # So we grab the expected module name from get_ext_filename and remove the extension
        # and we pass it to CMake to generate the module with the correct name
        # I don't know if this is the best way to do it, but it works.
        # Anybody with a better idea is welcome to contribute.
        full_module_name_with_ext = self.get_ext_filename(ext.name)
        full_module_name = os.path.splitext(full_module_name_with_ext)[0]

        cmake_args = [
            "-DPYVISION_DEBUG=%s" % ("ON" if cfg == "Debug" else "OFF"),
            f"-DDEVICE_C_EXT_NAME={full_module_name}",
            f"-DCMAKE_BUILD_TYPE={cfg}",
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}",
            f"-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_{cfg.upper()}={self.build_temp}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
        ]

        if platform.system() == "Windows":
            cmake_args += [
                "-DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=TRUE",
                f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}",
            ]

            plat = "x64" if platform.architecture()[0] == "64bit" else "Win32"

            if self.compiler.compiler_type == "msvc":
                cmake_args += [
                    f"-DCMAKE_GENERATOR_PLATFORM={plat}",
                ]
            else:
                # TODO: add support for other compilers
                pass

        cmake_args += cmake_cmd_args
        pprint(cmake_args)

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # Configure and build the extension
        subprocess.check_call(
            ["cmake", ext.cmake_lists_dir] + cmake_args, cwd=self.build_temp
        )
        subprocess.check_call(
            ["cmake", "--build", ".", "--config", cfg], cwd=self.build_temp
        )


setup_dir = pathlib.Path(__file__).parent.resolve()
pyproject_toml = setup_dir / "pyproject.toml"
with open(pyproject_toml, "rb") as f:
    tomli_dict = tomli.load(f)
    dependencies = tomli_dict["project"]["dependencies"]

    install_requires = [str(Requirement(line.strip())) for line in dependencies]

setup(
    name="pyvision",
    version=get_version(),
    description="Pyvision: a framework to detect objects",
    url="https://github.com/lion24/pyvision",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    ext_modules=[CMakeExtension(c_module_name)],
    cmdclass={"build_ext": CMakeBuild},
)
