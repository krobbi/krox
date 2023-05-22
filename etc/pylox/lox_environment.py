from lox_error_reporter import ErrorReporter
from lox_token import Token
from typing import Any, Self

class Environment:
    """ An environment of names and values. """
    
    error_reporter: ErrorReporter
    """ The environment's error reporter. """
    
    enclosing: Self | None
    """ The environment's enclosing environment. """
    
    values: dict[str, Any]
    """ The environment's names and values. """
    
    def __init__(
            self: Self, error_reporter: ErrorReporter,
            enclosing: Self | None = None) -> None:
        """ Initialize the environment. """
        
        self.error_reporter = error_reporter
        self.enclosing = enclosing
        self.values = {}
    
    
    def get(self: Self, name: Token) -> Any:
        """
        Get a value from the environment and throw an error if it is
        undefined.
        """
        
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        self.error_reporter.error(name, f"Undefined variable `{name.lexeme}`.")
        raise RuntimeError()
    
    
    def assign(self: Self, name: Token, value: Any) -> None:
        """ Assign a name and value in the environment. """
        
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
        else:
            self.error_reporter.error(
                    name, f"Undefined variable `{name.lexeme}`.")
            raise RuntimeError()
    
    
    def define(self: Self, name: str, value: Any) -> None:
        """ Define a name and value in the environment. """
        
        self.values[name] = value
    
    
    def ancestor(self: Self, distance: int) -> Self:
        """ Return the environment's ancestor at a distance. """
        
        environment: Environment = self
        
        for i in range(distance):
            if environment.enclosing is None:
                break
            
            environment = environment.enclosing
        
        return environment
    
    
    def get_at(self: Self, distance: int, name: str) -> Any:
        """
        Get a value from the environment's ancestor at a distance.
        """
        
        return self.ancestor(distance).values[name]
    
    
    def assign_at(self: Self, distance: int, name: Token, value: Any) -> None:
        """
        Assign a value in the environment's ancestor at a distance.
        """
        
        self.ancestor(distance).values[name.lexeme] = value
