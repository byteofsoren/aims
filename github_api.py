import os
import re

import requests

from colors import Colors
from config_manager import ConfigManager


def find_latest_file_name(local_repo, appimage_name):
    """
    Find the filename and the url on the remote GitHub page using regex.

    Args:
        local_repo (dict):  Is a dict containing information to retrive
                            file name.
        appimage_name (str):    is the name of the Appimage that we want to
                                find the most reasent file name of.

    Returns: filename, appimage_url
    """

    print(f"find_file_name {local_repo.path} with {appimage_name}")
    link = local_repo[appimage_name]['link']
    user, repo = link.split("/")
    link = link.replace("/", r"\/")
    filename_regex = local_repo[appimage_name]['regex']['filename']
    version_regex = local_repo[appimage_name]['regex']['version']
    # print(link, re.escape(link))

    # Download information from github
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error accessing the GitHub releases page")
        return

    # Save responce to a file for debugging.
    # with open("responce.html", "w") as htmlf:
    #     htmlf.write(response.text)

    pattern = r'https://github.com/' + link + r'\/releases\/download\/' + \
        version_regex + r'/' + filename_regex

    # Extract the correct AppImage link
    matches = re.findall(pattern, response.text)

    if not matches:
        print("No matching AppImage found on the releases page")
        print("DebugOutput")
        Colors.varprint(link, Colors.red)
        Colors.varprint(user, Colors.red)
        Colors.varprint(filename_regex, Colors.red)
        Colors.varprint(version_regex, Colors.red)
        Colors.varprint(url, Colors.red)
        return
    appimage_url = matches[0]
    matches = re.findall(filename_regex, appimage_url)
    if not matches:
        raise Exception("No matching AppImage found on the releases page")
    filename = matches[0]

    return filename, appimage_url


def get_github_data(local_repo, appimage_name):
    print(f"get_github_data {local_repo.path} with {appimage_name}")
    link = local_repo[appimage_name]['link']
    user, repo = link.split("/")
    link = link.replace("/", r"\/")

    # Download information from github
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error accessing the GitHub releases page")
        return

    # Save responce to a file for debugging.
    with open("responce.html", "w") as htmlf:
        htmlf.write(response.text)
    print(response.text)
    return response


def download_appimage(url, path, filename):
    full_path = os.path.join(path, filename)
    if not os.path.exists(path):
        raise Exception(f"Path did not exit {path}")
    try:
        responce = requests.get(url, stream=True)
        responce.raise_for_status()

        counter = 0
        with open(full_path, 'wb') as file:
            print("Downloading [", end="")
            for chunk in responce.iter_content(chunk_size=8192):
                counter += 1
                if counter > 100:
                    print(".", end="")
                    counter = 0
                file.write(chunk)
        print("]")
        print(f"AppImage downladed successfully: {full_path}")
    except Exception as e:
        print(f"Error downloading the file: {e}")
        raise e
