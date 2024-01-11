import os
import re
import stat
import textwrap

import yaml
from fuzzywuzzy import process

from colors import Colors
from config_manager import ConfigManager
from github_api import download_appimage, find_latest_file_name
from utils import ask


def install_appimage(appimage_name: str, repo: ConfigManager):
    """
    Installs the AppImage from github.

    Args:
        appimage_name (str): Name or key for the Appimage to be installed
        repo (dict): Link to the repo
    """
    if appimage_name not in repo.keys():
        raise Exception(f"Name: {appimage_name} is not in repo")
    app = repo[appimage_name]
    filename_regex = app['regex']['filename']
    version_regex = app['regex']['version']

    # Contact GitHub and get the latest filename and url
    filename, url = find_latest_file_name(repo, appimage_name)
    version = re.findall(version_regex, filename)

    # Load the configuration files
    print(f"Found {filename} at {url}")
    config = ConfigManager('config.yaml')
    installed_appimages_file = os.path.expanduser(
        config['yamls']['installed_appimages'])
    install_diretory = os.path.dirname(installed_appimages_file)
    if not os.path.exists(install_diretory):
        os.makedirs(install_diretory)
    installed_appimages = ConfigManager(installed_appimages_file)

    # Derive the local path for the placement of the file.
    # It becomes someting like $HOME/bin/AppImage_name
    path = os.path.expanduser(
        config['sysconfig']['user_path']) + app['installation']['path'] + "/"
    user_path = os.path.expanduser(config['sysconfig']['user_path'])

    # Create a path to where the file should be downloaded to.
    local_file_path = os.path.join(path, filename)

    if not os.path.exists(path):
        # Make path no package installed
        print("No path existed")
        os.makedirs(path)

    if os.path.exists(path) and os.path.isdir(path):
        # Package was already installed check files.
        print("Path existed checking files")

        file_path_exist = os.path.exists(local_file_path)
        file_path_isfile = os.path.exists(local_file_path)

        if file_path_exist and file_path_isfile:
            print("File existed. Same version do nothing.")
            return
        elif file_path_exist and not file_path_isfile:
            print("File was not a file ERROR")
            return

        # Get all files in in the path diretory.
        matching_files = find_matching_files(path, filename_regex)
        # Remove the old AppImages
        print("Removing old AppImages")
        for file in matching_files:
            print(".", end='')
            full_path = os.path.join(path, file)
            os.remove(full_path)
        print("]")

        # Download the image form GitHub
        download_appimage(url, path, filename)

        # Set the right premissions.
        print(local_file_path)
        st = os.stat(local_file_path)
        os.chmod(local_file_path, st.st_mode | stat.S_IEXEC)

        # Create a symlink from
        sym_target = os.path.join(
            user_path, appimage_name.lower())
        try:
            if os.path.exists(sym_target) and os.path.islink(sym_target):
                print("Path existed and is alink removed link")
                os.remove(sym_target)

            if os.path.exists(sym_target) and os.path.isdir(sym_target):
                print("Target path and the stored dir has the same name")
                os.symlink(local_file_path, f"{sym_target}_app")
            elif os.path.exists(sym_target) and not os.path.islink(sym_target):
                raise Exception("Path existed but was not a symlink")
            else:
                os.symlink(local_file_path, sym_target)
        except OSError as e:
            raise Exception(f"OSError {e}")

        # Add packages installed to the installedrepos.yaml
        installed_appimages[appimage_name] = {
            'installed_version': version,
            'filename': filename,
            'path': local_file_path,
            'symlink': sym_target,
            'url': url
        }
        installed_appimages.save()


def load_installed_images():
    """
    Loads the installed appimages yaml file and returns the dict

    Returns Installed appimages (dict):
    """
    config = ConfigManager('config.yaml')
    # Load the installed_appimages yaml file
    installed_appimages_file = os.path.expanduser(
        config['yamls']['installed_appimages'])
    install_diretory = os.path.dirname(installed_appimages_file)
    if not os.path.exists(install_diretory):
        raise Exception(f"File {installed_appimages_file} did not exists")
    installed_appimages = ConfigManager(installed_appimages_file)
    return installed_appimages


def remove_appimage(appimage_name: str):
    """
    Removes an installed app image.

    Arguments:
        appimage_name (str): Name of the appimage to be removed
    """
    # Check and load installed appimages yaml file.
    try:
        installed_appimages = load_installed_images()
    except Exception as e:
        raise e

    # Check if the appimages exist in the installed..yaml file
    if appimage_name not in installed_appimages.keys():
        raise Exception(f"The {appimage_name} was not installed")

    # Get app and path
    app = installed_appimages[appimage_name]
    path = app['path']
    symlink = app['symlink']

    # Check and remove the symlink
    if os.path.exists(symlink) and os.path.islink(symlink):
        os.unlink(symlink)
    else:
        print("No symlink was found, continuing")

    # Remove old AppImage
    if os.path.exists(path) and os.path.isfile(path):
        print(f"Removing file {path}")
        try:
            os.remove(path)
        except PermissionError as pe:
            print(f"Could not remove {path} {pe}")
            raise pe
    elif os.path.exists(app) and os.path.isdir(path):
        raise Exception("Wrong installation target to remove")

    print("Removing entry {appimage_name} from installed AppImages")
    del installed_appimages[appimage_name]

    # Save changes to the installed appimages yaml file.
    installed_appimages.save()
    print(f"Done removing {appimage_name}")


def find_matching_files(directory_path, filename_regex):
    matching_files = list()
    pattern = re.compile(filename_regex)

    print("Matching filenames [")
    for entry in os.listdir(directory_path):
        print('.', end='.')
        full_path = os.path.join(directory_path, entry)
        if os.path.isfile(full_path) and pattern.match(entry):
            matching_files.append(entry)

    print(']')
    return matching_files


def update_appimage(repo):
    """
    Updates the installed appimages that are tracked by the system.

    Arguments:
        repo (dict): Is use to find latest file name and
                     where to download them.
    """

    # Check and load installed appimages yaml file.
    try:
        installed_appimages = load_installed_images()
    except Exception as e:
        raise e
    # app = installed_appimages[appimage_name]
    for appimage_name in installed_appimages.keys():
        print(f"Checking {appimage_name}")
        app = installed_appimages[appimage_name]
        installed_appimage_file_name = app['filename']

        # Find latest file name
        newer_filename, url = find_latest_file_name(repo, appimage_name)
        if not newer_filename:
            raise Exception(
                f"Filename: `{newer_filename}` is empty, do nothing")
        # Compare it with installed
        if installed_appimage_file_name.lower() == newer_filename.lower():
            print("Both are equal, no update")
            break
        print(f"Removing the older AppImage {installed_appimage_file_name}")
        remove_appimage(appimage_name)
        print(f"Installing the newer AppImage {newer_filename}")
        install_appimage(appimage_name)


def search_appimages(search_term: str, repos: dict):
    """
    Searches for AppImmages that can be installed by this system.
    Prints out a formatted list of search hits.

    Arguments:
        search_term (str): What is searched for.
        repos (dict): Where to search.
    """
    simplified = dict()
    for app in repos.keys():
        simplified[app] = repos[app]['description']

    # Fuzzy search the flattened list
    results = process.extractBests(
        search_term, simplified, limit=10, score_cutoff=50)

    # Keep track of matched AppImages to avoid double reporting
    # matched_appimages = set()
    # matched_description = dict()

    pruned_results = dict()
    for result in results:
        description = result[0]
        quality = result[1]
        name = result[2]
        if quality > 55:
            pruned_results[name] = description

    for app in pruned_results.keys():
        print("")
        print(f"{Colors.blue}{app}{Colors.reset}")
        text = pruned_results[app]
        print(textwrap.fill(text,
                            initial_indent="  ", subsequent_indent="  "))


def show_installed_appimages():
    """
    Shows a list of appimages that the system aim tracks.
    """
    try:
        installed_appimages = load_installed_images()
    except Exception as e:
        raise e
    for app in installed_appimages.keys():
        meta = installed_appimages[app]
        # breakpoint()
        print(f"{Colors.yellow}{app}{Colors.reset}")
        print(f" FileName: {Colors.blue}{meta['filename']}{Colors.reset}")
        print(f" Symlink: {Colors.cyan}{meta['symlink']}{Colors.reset}")
