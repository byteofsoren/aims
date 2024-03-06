from colors import Colors


class Status(object):
    """docstring for Status"""

    messages: list = []

    @staticmethod
    def show():
        for message in Status.messages:
            print(message)

    @staticmethod
    def varprint(varstr: str):
        """
        varprint
        Call this function like this
        Colors.varprint(f"{variable=}")
        """
        varname, value = varstr.split('=')
        return f"{varname}{Colors.cyan(value)}"

    @staticmethod
    def symlink(message, symlink: str):
        mes = f"[{Colors.yellow}INFO{Colors.reset}] {message} \
                {Colors.cyan(symlink)}"
        Status.messages.append(mes)
        return mes

    @staticmethod
    def url(message, url):
        mes = f"[{Colors.yellow()}INFO{Colors.reset}] "
        mes += f"{message} URL = {Colors.blue(url)}"
        Status.messages.append(mes)
        return mes

    @staticmethod
    def ok(message, *args):
        rest = " ".join([x for x in args])
        mes = f'[{Colors.green()}OK{Colors.reset}] {message} {rest}'
        Status.messages.append(mes)
        return mes

    @staticmethod
    def info(message, *args):
        rest = "\n\t".join([x for x in args])
        mes = f'[{Colors.yellow()}INFO{Colors.reset}] {message} {rest}'
        Status.messages.append(mes)
        return mes

    @staticmethod
    def error(message, *args):
        rest = "\n\t".join([str(x) for x in args])
        mes = f'[{Colors.red()}ERROR{Colors.reset}]{Colors.red()} {message}\
                \n\t{rest}{Colors.reset}'
        Status.messages.append(mes)
        return mes
