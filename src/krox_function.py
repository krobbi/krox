from collections.abc import Callable
from krox_callable import KroxCallable
from krox_environment import Environment
from krox_error_reporter import ErrorReporter
from krox_stmt import FunctionStmt, Stmt
from typing import Any, Self

class ReturnException(Exception):
    """ An exception containing a return value from a function call. """
    
    value: Any
    """ The return value. """
    
    def __init__(self: Self, value: Any) -> None:
        """ Initialize the return exception. """
        
        super().__init__()
        self.value = value


class KroxFunction(KroxCallable):
    """ A user-defined Krox function. """
    
    error_reporter: ErrorReporter
    """ The function's error reporter. """
    
    closure: Environment
    """ The function's closure. """
    
    executor: Callable[[list[Stmt], Environment], None]
    """ The function's executor. """
    
    declaration: FunctionStmt
    """ The function's declaration. """
    
    is_initializer: bool
    """ Whether the function is an initializer. """
    
    def __init__(
            self: Self, error_reporter: ErrorReporter,
            executor: Callable[[list[Stmt], Environment], None],
            declaration: FunctionStmt, closure: Environment,
            is_initializer: bool) -> None:
        """ Initialize the function. """
        
        super().__init__()
        self.error_reporter = error_reporter
        self.executor = executor
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer
    
    
    def __repr__(self: Self) -> str:
        """ Represent the function as a string. """
        
        return f"<fn {self.declaration.name.lexeme}>"
    
    
    def arity(self: Self) -> int:
        """ Return the function's arity. """
        
        return len(self.declaration.params)
    
    
    def call(self: Self, arguments: list[Any]) -> None:
        """ Call the function and return its return value. """
        
        environment: Environment = Environment(
                self.error_reporter, self.closure)
        
        for index, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[index])
        
        try:
            self.executor(self.declaration.body, environment)
        except ReturnException as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            
            return return_value.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        
        return None
