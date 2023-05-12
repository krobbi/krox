from typing import Any, Self

class LoxCallable:
    """ An object that is callable by Lox. """
    
    def arity(self: Self) -> int:
        """ Return the Lox callable's arity. """
        
        return 0
    
    
    def call(
            self: Self, arguments: list[Any]) -> Any:
        """ Call the Lox callable and return a value. """
        
        pass
