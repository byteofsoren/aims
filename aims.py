import argparse
import pdb

from colors import Colors
from config_manager import ConfigManager
from github_api import find_latest_file_name, get_github_data
from repo_manager import (install_appimage, remove_appimage, search_appimages,
                          show_installed_appimages, update_appimage)
from status import Status


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="AppImage Manager for Linux (AIM)")
    parser.add_argument(
        'action', help="Action to perform: \
                search, install, update, remove, show and debug")
    parser.add_argument(
        '-n', '--name', help="Name of the AppImage in the official repos",
        default=None)
    parser.add_argument(
        '-N', '--Name', help="Name of the AppImage in the personal repo",
        default=None)
    args = parser.parse_args()

    # Load configuration and repository data
    # config = ConfigManager('config.yaml') # Not used right now
    official_repos = ConfigManager('repos.yaml')

    try:
        personal_repos = ConfigManager('personalrepos.yaml')
    except Exception:
        # personal_repos = None
        Status.info("Personal repos not used")

    # try:
    #     installed_appimages_file = config['ymls']['installed_appimages']
    #     installed_repos = ConfigManager(installed_appimages_file)
    #     print(installed_repos)
    # except Exception:
    #     print("No installed repos")

    # Perform actions based on arguments
    if args.action == 'search':
        if args.name:
            search_appimages(args.name, official_repos)
        elif args.Name:
            if len(personal_repos) == 0:
                print("Personla repo has no entries")
                return
            search_appimages(args.name, personal_repos)
        else:
            print("Please specify the name of the AppImage to search.")
    # INSTALL
    elif args.action == 'install':
        if args.name:
            try:
                install_appimage(args.name, official_repos)
            except Exception as e:
                Status.error("Exception: ", e)
                Status.show()
                raise e
        elif args.Name:
            if len(personal_repos) == 0:
                Status.error("Personla repo has no entries")
                Status.show()
                return
                # install_appimage(args.name, official_repo,\
                # personal_repos, config)
        else:
            print("Please specify the name of the AppImage to install.")

    elif args.action == 'debug':
        if args.name:
            get_github_data(official_repos, args.name)
            try:
                fname, url = find_latest_file_name(official_repos, args.name)
            except TypeError:
                Status.error("Type error of find_latest_file_name() function")
                Status.show()
                return
            # print("Fond this:")
            # print(f"File name: {Colors.yellow()}{fname}{Colors.reset}")
            # print(f"url:{Colors.blue()}{url}{Colors.reset}")
            Status.show()
            if fname:
                print(f"{Colors.green()}OK{Colors.reset} it worked")

    elif args.action == 'update':
        update_appimage(official_repos)

    elif args.action == 'remove':
        if args.name:
            remove_appimage(args.name)
        if args.Name:
            pass
        else:
            print("Please specify the name of the AppImage to update.")

    elif args.action == 'show':
        try:
            show_installed_appimages()
        except Exception as e:
            Status.error("Show_installed_appimages errored out")
            Status.show()
            raise e

    else:
        print("Invalid action. Please choose ether:")
        print("\tsearch -n [name of package]")
        print("\tinstall -n [name of package]")
        print("\tupdate")
        print("\tremove")
        print("\tshow")


if __name__ == "__main__":
    main()
    # Status.show()
