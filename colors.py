import yaml


class Colors(object):

    # """Docstring for Color. """
    # black = '\033[0;30m'
    # red = '\033[0;31m'
    # green = '\033[0;32m'
    # yellow = '\033[0;33m'
    # blue = '\033[0;34m'
    # magenta = '\033[0;35m'
    # cyan = '\033[0;36m'
    # white = '\033[0;37m'
    # reset = '\033[0m'

    reset = '\033[0m'

    @staticmethod
    def _gettext_(c, text=None):
        if text is None:
            return c
        else:
            return f'{c}{text}{Colors.reset}'

    @staticmethod
    def black(text=None):
        return Colors._gettext_('\033[0;30m', text)

    @staticmethod
    def red(text=None):
        return Colors._gettext_('\033[0;31m', text)

    @staticmethod
    def green(text=None):
        return Colors._gettext_('\033[0;32m', text)

    @staticmethod
    def yellow(text=None):
        return Colors._gettext_('\033[0;33m', text)

    @staticmethod
    def blue(text=None):
        return Colors._gettext_('\033[0;34m', text)

    @staticmethod
    def magneta(text=None):
        return Colors._gettext_('\033[0;35m', text)

    @staticmethod
    def cyan(text=None):
        return Colors._gettext_('\033[0;36m', text)

    @staticmethod
    def white(text=None):
        return Colors._gettext_('\033[0;37m', text)
