from collections.abc import Callable
from lox_callable import LoxCallable
from typing import Any, Self

class NativeFunction(LoxCallable):
    """ A function that is native to Lox. """
    
    parameter_count: int
    """ The native function's parameter count. """
    
    driver: Callable[[list[Any]], Any]
    """ The native function's driver function. """
    
    def __init__(
            self: Self, parameter_count: int,
            driver: Callable[[list[Any]], Any]) -> None:
        """ Initialize the native function. """
        
        super().__init__()
        self.parameter_count = parameter_count
        self.driver = driver
    
    
    def __repr__(self: Self) -> str:
        """ Represent the native function as a string. """
        
        return "<native fn>"
    
    
    def arity(self: Self) -> int:
        """ Return the native function's arity. """
        
        return self.parameter_count
    
    
    def call(self: Self, arguments: list[Any]) -> Any:
        """
        Call the native function's driver function and return a value.
        """
        
        return self.driver(arguments)
