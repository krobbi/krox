from lox_class import LoxClass
from lox_error_reporter import ErrorReporter
from lox_environment import Environment
from lox_function import LoxFunction
from lox_token import Token
from typing import Any, Self

class LoxInstance:
    """ An instance of a user-defined class. """
    
    error_reporter: ErrorReporter
    """ The instance's error reporter. """
    
    klass: LoxClass
    """ The instance's class. """
    
    fields: dict[str, Any]
    """ The instance's fields. """
    
    def __init__(
            self: Self,
            error_reporter: ErrorReporter, klass: LoxClass) -> None:
        """ Initialize the instance. """
        
        self.error_reporter = error_reporter
        self.klass = klass
        self.fields = {}
    
    
    def __repr__(self: Self) -> str:
        """ Represent the instance as a string. """
        
        return f"{self.klass.name} instance"
    
    
    def get(self: Self, name: Token) -> Any:
        """ Get a property from the instance. """
        
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        method: LoxFunction | None = self.klass.find_method(name.lexeme)
        
        # Move binding here as a workaround for circular imports.
        if method is not None:
            return self.bind_method(method)
        
        self.error_reporter.error(name, f"Undefined property `{name.lexeme}`.")
        raise RuntimeError()
    
    
    def set(self: Self, name: Token, value: Any) -> None:
        """ Set a field on the instance. """
        
        self.fields[name.lexeme] = value
    
    
    def bind_method(self: Self, method: LoxFunction) -> LoxFunction:
        """ Create a new method bound to this instance. """
        
        environment: Environment = Environment(
                self.error_reporter, method.closure)
        environment.define("this", self)
        return LoxFunction(
                self.error_reporter, method.executor,
                method.declaration, environment, method.is_initializer)
