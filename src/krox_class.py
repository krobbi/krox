from krox_callable import KroxCallable
from krox_error_reporter import ErrorReporter
from krox_function import KroxFunction
from typing import Any, Self

class KroxClass(KroxCallable):
    """ A user-defined Krox class. """
    
    error_reporter: ErrorReporter
    """ The class' error reporter. """
    
    name: str
    """ The class' name. """
    
    methods: dict[str, KroxFunction]
    """ The class' methods. """
    
    def __init__(
            self: Self, error_reporter: ErrorReporter,
            name: str, methods: dict[str, KroxFunction]) -> None:
        """ Initialize the class. """
        
        super().__init__()
        self.error_reporter = error_reporter
        self.name = name
        self.methods = methods
    
    
    def __repr__(self: Self) -> str:
        """ Represent the class as a string. """
        
        return self.name
    
    
    def arity(self: Self) -> int:
        """ Return the class' arity. """
        
        initializer: KroxFunction | None = self.find_method("init")
        
        if initializer is None:
            return 0
        else:
            return initializer.arity()
    
    
    def call(self: Self, arguments: list[Any]) -> Any:
        """ Call the class and return a new instance. """
        
        # Workaround for circular import.
        from krox_instance import KroxInstance
        
        instance: KroxInstance = KroxInstance(self.error_reporter, self)
        initializer: KroxFunction | None = self.find_method("init")
        
        if initializer is not None:
            instance.bind_method(initializer).call(arguments)
        
        return instance
    
    
    def find_method(self: Self, name: str) -> KroxFunction | None:
        """ Find a method from its name. """
        
        if name in self.methods:
            return self.methods[name]
        
        return None
