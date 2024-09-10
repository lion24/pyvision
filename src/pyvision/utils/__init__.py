"""Utility functions mainly to download dependencies from internet."""

import os
import zipfile

import requests
from tqdm import tqdm


def check_file_exists(path: str) -> bool:
    """Check if a file exists at the given path.

    Args:
        path (str): The path to check.
    """
    return os.path.exists(path)


def download_to(path: str, url: str):
    """Download a file from the given URL to the specified path.

    Args:
        path (str): The path to save the downloaded file.
        url (str): The URL to download the file from.
    """
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    chunk_size = 1024
    print(f"Downloading to {path}")

    with (
        open(path, "wb") as file,
        tqdm(
            desc="Downloading",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=chunk_size,
        ) as bar,
    ):
        for data in response.iter_content(chunk_size):
            file.write(data)
            bar.update(len(data))


def extract_to(path: str, dest: str):
    """Extract a zip file to the specified destination.

    Args:
        path (str): The path to the zip file.
        dest (str): The path to extract the zip file to.
    """
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(dest)
