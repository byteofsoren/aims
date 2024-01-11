

def ask(prompt: str, options: list):
    default = 'N'
    for option in options:
        if option[0].isupper():
            default = option
    res = input(f"{prompt}{', '.join(options)}: ")
    if len(res) == 0:
        return default
    for option in options:
        if res.lower() == option.lower():
            return option

    return default
