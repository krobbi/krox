from collections.abc import Callable
from sys import argv
from typing import Any

def argc_extension(arguments: list[Any]) -> float:
    """ The argc extension. """
    
    return float(max(len(argv) - 1, 0))


def argv_extension(arguments: list[Any]) -> str | None:
    """ The argv extension. """
    
    index: int = int(arguments[0]) + 1
    
    if index < 1 or index >= len(argv):
        return None
    
    return argv[index]


def install_extensions(
        define_native: Callable[
                [str, int, Callable[[list[Any]], Any]], None]) -> None:
    """ Install the extensions. """
    
    define_native("argc", 0, argc_extension)
    define_native("argv", 1, argv_extension)
