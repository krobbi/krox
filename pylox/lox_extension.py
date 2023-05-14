from lox_environment import Environment
from lox_native_function import NativeFunction
from sys import argv
from typing import Any, Self

class ArgcExtension(NativeFunction):
    """ The argc extension. """
    
    def __init__(self: Self, environment: Environment) -> None:
        """ Initialize the argc extension. """
        
        super().__init__(0, "argc", environment)
    
    
    def call(self: Self, arguments: list[Any]) -> float:
        """
        Call the argc extension and return the number of command line arguments.
        """
        
        return float(max(len(argv) - 1, 0))


class ArgvExtension(NativeFunction):
    """ The argv extension. """
    
    def __init__(self: Self, environment: Environment) -> None:
        """ Initialize the argv extension. """
        
        super().__init__(1, "argv", environment)
    
    
    def call(self: Self, arguments: list[Any]) -> str | None:
        """
        Call the argv extension and return the command line argument at an
        index.
        """
        
        index: int = int(arguments[0]) + 1
        
        if index < 1 or index >= len(argv):
            return None
        
        return argv[index]


def install_extensions(environment: Environment) -> None:
    """ Install the extensions to an environment. """
    
    ArgcExtension(environment)
    ArgvExtension(environment)
