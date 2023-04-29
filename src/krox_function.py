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
    
    def __init__(
            self: Self, error_reporter: ErrorReporter, closure: Environment,
            executor: Callable[[list[Stmt], Environment], None],
            declaration: FunctionStmt) -> None:
        """ Initialize the function. """
        
        super().__init__()
        self.error_reporter = error_reporter
        self.closure = closure
        self.executor = executor
        self.declaration = declaration
    
    
    def __repr__(self: Self) -> str:
        """ Represent the function as a string. """
        
        return f"<fn {self.declaration.name.lexeme}>"
    
    
    def arity(self: Self) -> int:
        """ Return the function's arity. """
        
        return len(self.declaration.params)
    
    
    def call(self: Self, arguments: list[Any]) -> None:
        """ Call the function and return nil. """
        
        environment: Environment = Environment(
                self.error_reporter, self.closure)
        
        for index, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[index])
        
        try:
            self.executor(self.declaration.body, environment)
        except ReturnException as return_value:
            return return_value.value
        
        return None
