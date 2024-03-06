import os
import re

import requests

from colors import Colors
from config_manager import ConfigManager
from status import Status


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
    Status.info("Link=", link)
    user, repo = link.split("/")
    Status.info(f"GitHub {user=}, {repo=}")
    split_link = link.replace("/", r"\/")
    Status.info("Replaced / with \/ Link=", split_link)
    filename_regex = local_repo[appimage_name]['regex']['filename']
    version_regex = local_repo[appimage_name]['regex']['version']

    # Download information from github
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    Status.url("GitHub", url)

    response = requests.get(url)
    Status.info(f"{response.status_code=}")
    if response.status_code != 200:
        Status.error("Error: Did not get html data",
                     response.status_code)
        return

    # Save responce to a file for debugging.
    # with open("responce.html", "w") as htmlf:
    #     htmlf.write(response.text)

    pattern = r'https://github.com/' + split_link + \
        r'\/releases\/download\/' + \
        version_regex + r'/' + filename_regex
    Status.info(f"{pattern=}")

    # Extract the correct AppImage link
    matches = re.findall(pattern, response.text)

    if not matches:
        print(response.text)
        Status.error("No matching AppImage found!",
                     f"Tweek the regex for {link} AppImage")
        raise ValueError("No matching AppImage found on the releases page")
    Status.info(f"Found {len(matches)} st matches")
    appimage_url = matches[0]
    matches = re.findall(filename_regex, appimage_url)
    filename = matches[0]
    Status.info(f"{filename=}; {appimage_url=}")

    return filename, appimage_url


def get_github_data(local_repo, appimage_name):
    print(f"get_github_data {local_repo.path} with {appimage_name}")
    if appimage_name not in local_repo:
        print(f"{Colors.yellow()}The name {Colors.blue()}{appimage_name}\
                {Colors.yellow()} does not exist in the \
                data base{Colors.reset}")
        raise ValueError
    link = local_repo[appimage_name]['link']
    user, repo = link.split("/")
    # split_link = link.replace("/", r"\/")

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
