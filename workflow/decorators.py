from workflow.constants import (
    CONSOLE_GREEN_COLOR,
    CONSOLE_BLUE_COLOR,
    CONSOLE_BLUE2_COLOR
)


def print_action_decorator(function):
    def wrapper(*args, **kwargs):
        string_separator = f"{'*' * 30}\n"
        value = function(*args, **kwargs)
        print(
            f"{string_separator}"
            f"{CONSOLE_GREEN_COLOR}"
            f"[ACTION] {function.__name__}()\n"
            f"{CONSOLE_BLUE_COLOR}"
            f'    Params = {kwargs}\n'
            f"{CONSOLE_BLUE2_COLOR}"
            f'    Result = {value}\n'
            f"{string_separator}\n"
        )
        return value
    return wrapper
