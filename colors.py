import yaml


class Colors(object):

    """Docstring for Color. """
    black = '\033[0;30m'
    red = '\033[0;31m'
    green = '\033[0;32m'
    yellow = '\033[0;33m'
    blue = '\033[0;34m'
    magenta = '\033[0;35m'
    cyan = '\033[0;36m'
    white = '\033[0;37m'
    reset = '\033[0m'

    @staticmethod
    def varprint(var, color):
        var, value = f"{var=}".split('=')
        print(f"{Colors.blue}{var}{Colors.reset}={color}{value}{Colors.reset}")
