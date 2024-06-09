import os
import re
import stat
import textwrap

import yaml
from fuzzywuzzy import process

from colors import Colors
from config_manager import ConfigManager
from github_api import download_appimage, find_latest_file_name
from status import Status
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
    try:
        filename, url = find_latest_file_name(repo, appimage_name)
        Status.url("latest file name url", url)
        Status.filename(filename, "find_latest_file_name")
    except ValueError as ve:
        Status.error(
            "repo_manager.py install_appimage did",
            "not find a appimage on GitHub")
        raise ve
    version = re.findall(version_regex, filename)

    # Load the configuration files
    # Status.info(f"Found {filename} at {url}")
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
    # user_path = os.path.expanduser(config['sysconfig']['user_path'])
    symlink_path = os.path.expanduser(config['sysconfig']['symlink_path'])

    # Create a path to where the file should be downloaded to.
    local_file_path = os.path.join(path, filename)

    if not os.path.exists(path):
        # Make path no package installed
        # Status.info("No path existed")
        os.makedirs(path)

    if os.path.exists(path) and os.path.isdir(path):
        # Package was already installed check files.
        # Status.info("Path existed checking files")

        file_path_exist = os.path.exists(local_file_path)
        file_path_isfile = os.path.exists(local_file_path)

        if file_path_exist and file_path_isfile:
            # Status.info("File existed. Same version do nothing.")
            return
        elif file_path_exist and not file_path_isfile:
            # Status.info("File was not a file ERROR")
            return

        # Get all files in in the path diretory.
        matching_files = find_matching_files(path, filename_regex)
        Status.info(f"Found {len(matching_files)} matching files in the repo")
        # if not matching_files:
        #     raise ValueError("Matching files list is empty")
        # Remove the old AppImages
        # Status.info("Removing old AppImages")
        for file in matching_files:
            # Status.info(".", end='')
            full_path = os.path.join(path, file)
            os.remove(full_path)
        # Status.info("]")

        # Download the image form GitHub
        download_appimage(url, path, filename)

        # Set the right premissions.
        # Status.info(local_file_path)
        st = os.stat(local_file_path)
        os.chmod(local_file_path, st.st_mode | stat.S_IEXEC)

        # Create a symlink from
        sym_target = os.path.join(
            symlink_path, appimage_name.lower())
        try:
            if os.path.exists(sym_target) and os.path.islink(sym_target):
                # Status.info(
                #     "Path existed and is alink, \
                #      removed link to cerate new link")
                os.remove(sym_target)

            if os.path.exists(sym_target) and os.path.isdir(sym_target):
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
        Status.info("No symlink was found, continuing")

    # Remove old AppImage
    if os.path.exists(path) and os.path.isfile(path):
        Status.info(f"Removing file {path}")
        try:
            os.remove(path)
        except PermissionError as pe:
            Status.error(f"Could not remove {path} {pe}")
            raise pe
    elif os.path.exists(app) and os.path.isdir(path):
        raise Exception("Wrong installation target to remove")

    Status.info("Removing entry {appimage_name} from installed AppImages")
    del installed_appimages[appimage_name]

    # Save changes to the installed appimages yaml file.
    installed_appimages.save()
    Status.info(f"Done removing {appimage_name}")


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

    if len(matching_files) > 0:
        Status.ok(f"Found {len(matching_files)} st matching files")
    else:
        Status.error("Found no matching files")
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
    updated = False
    for appimage_name in installed_appimages.keys():
        Status.info(f"Checking {Colors.blue()}{appimage_name}{Colors.reset}")
        app = installed_appimages[appimage_name]
        installed_appimage_file_name = app['filename']

        # Find latest file name
        newer_filename, url = find_latest_file_name(repo, appimage_name)
        if not newer_filename:
            raise Exception(
                f"Filename: `{newer_filename}` is empty. \
                        Probably problem with the regular expression")
        # Compare it with installed
        if installed_appimage_file_name.lower() == newer_filename.lower():
            Status.info("Both are equal, no update")
            continue
        Status.info("Updating")
        updated = True
        Status.info(
            f"1. Removing the older AppImage {installed_appimage_file_name}")
        remove_appimage(appimage_name)
        Status.info(f"2. Installing the newer AppImage {newer_filename}")
        install_appimage(appimage_name, repo)
        Status.info("3. Done")
    if updated:
        Status.info("Packages where updated")
    else:
        Status.info("No packages to update")


def search_appimages(search_term: str, repos: dict):
    """
    Searches for AppImmages that can be installed by this system.
    Status.infos out a formatted list of search hits.

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
        Status.info("")
        print(f"{Colors.blue()}{app}{Colors.reset}")
        text = pruned_results[app]
        print(textwrap.fill(text,
                            initial_indent="  ", subsequent_indent="  "))


def show_installed_appimages():
    """
    Shows a list of appimages that the system aim tracks.
    """
    try:
        Status.info("Loading installed appimages")
        installed_appimages = load_installed_images()
        Status.info("Found {len(installed_appimages)}st installed images")

    except Exception as e:
        Status.error("Loading of installed appimages errored out")
        raise e
    for app in installed_appimages.keys():
        meta = installed_appimages[app]
        print(f"{Colors.yellow()}{app}{Colors.reset}")
        print(
            f" FileName: {Colors.blue()}{meta['filename']}{Colors.reset}")
        print(
            f" Symlink: {Colors.cyan()}{meta['symlink']}{Colors.reset}")
