from typing import Any, Self

class KroxCallable:
    """ An object that is callable by Krox. """
    
    def arity(self: Self) -> int:
        """ Return the Krox callable's arity. """
        
        return 0
    
    
    def call(
            self: Self, arguments: list[Any]) -> Any:
        """ Call the Krox callable and return a value. """
        
        pass
