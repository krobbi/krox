from lox_callable import LoxCallable
from lox_error_reporter import ErrorReporter
from lox_function import LoxFunction
from typing import Any, Self

class LoxClass(LoxCallable):
    """ A user-defined Lox class. """
    
    error_reporter: ErrorReporter
    """ The class' error reporter. """
    
    name: str
    """ The class' name. """
    
    superclass: Self | None
    """ The class' superclass. """
    
    methods: dict[str, LoxFunction]
    """ The class' methods. """
    
    def __init__(
            self: Self, error_reporter: ErrorReporter, name: str,
            superclass: Self | None, methods: dict[str, LoxFunction]) -> None:
        """ Initialize the class. """
        
        super().__init__()
        self.error_reporter = error_reporter
        self.name = name
        self.superclass = superclass
        self.methods = methods
    
    
    def __repr__(self: Self) -> str:
        """ Represent the class as a string. """
        
        return self.name
    
    
    def arity(self: Self) -> int:
        """ Return the class' arity. """
        
        initializer: LoxFunction | None = self.find_method("init")
        
        if initializer is None:
            return 0
        else:
            return initializer.arity()
    
    
    def call(self: Self, arguments: list[Any]) -> Any:
        """ Call the class and return a new instance. """
        
        # Workaround for circular import.
        from lox_instance import LoxInstance
        
        instance: LoxInstance = LoxInstance(self.error_reporter, self)
        initializer: LoxFunction | None = self.find_method("init")
        
        if initializer is not None:
            instance.bind_method(initializer).call(arguments)
        
        return instance
    
    
    def find_method(self: Self, name: str) -> LoxFunction | None:
        """ Find a method from its name. """
        
        if name in self.methods:
            return self.methods[name]
        
        if self.superclass is not None:
            return self.superclass.find_method(name)
        
        return None
