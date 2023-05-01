from krox_callable import KroxCallable
from krox_environment import Environment
from time import perf_counter
from typing import Any, Self

def stringify(value: Any) -> str:
    """ Convert a Krox value to a string. """
    if value is True:
        return "true"
    elif value is False:
        return "false"
    elif value is None:
        return "nil"
    elif isinstance(value, float):
        text: str = str(value)
        
        if text == "-0.0":
            return "0"
        elif text.endswith(".0"):
            return text[:-2]
        else:
            return text
    else:
        return str(value)


class NativeFunction(KroxCallable):
    """ A function that is native to Krox. """
    
    parameter_count: int
    """ The native function's parameter count. """
    
    def __init__(
            self: Self,
            parameter_count: int, name: str, environment: Environment) -> None:
        """ Initialize the native function. """
        
        super().__init__()
        self.parameter_count = parameter_count
        environment.define(name, self)
    
    
    def __repr__(self: Self) -> str:
        """ Represent the native function as a string. """
        
        return "<native fn>"
    
    
    def arity(self: Self) -> int:
        """ Return the native function's arity. """
        
        return self.parameter_count


class ClockNativeFunction(NativeFunction):
    """ The native clock function. """
    
    start: float
    """ The native clock function's starting time. """
    
    def __init__(self: Self, environment: Environment) -> None:
        """ Initialize the native clock function. """
        
        super().__init__(0, "clock", environment)
        self.start = perf_counter()
    
    
    def call(self: Self, arguments: list[Any]) -> float:
        """
        Call the native clock function and return the time in seconds
        since the starting time.
        """
        
        return perf_counter() - self.start


class InputNativeFunction(NativeFunction):
    """ The native input function. """
    
    def __init__(self: Self, environment: Environment) -> None:
        """ Initialize the native input function. """
        
        super().__init__(1, "input", environment)
    
    
    def call(self: Self, arguments: list[Any]) -> str:
        """ Call the native input function and return a string. """
        
        return input(stringify(arguments[0]))


class PrintNativeFunction(NativeFunction):
    """ The native print function. """
    
    def __init__(self: Self, environment: Environment) -> None:
        """ Initialize the native print function. """
        
        super().__init__(1, "print", environment)
    
    
    def call(self: Self, arguments: list[Any]) -> None:
        """ Call the native print function and return nil. """
        
        print(stringify(arguments[0]))
        return None


def install_native_functions(environment: Environment) -> None:
    """ Install the native functions to an environment. """
    
    ClockNativeFunction(environment)
    InputNativeFunction(environment)
    PrintNativeFunction(environment)
