from typing import Self

class ErrorReporter:
    """ Reports syntax errors. """
    
    error_count: int = 0
    """ The number of syntax errors that have been reported. """
    
    def report(self: Self, line: int, message: str, where: str = "") -> None:
        """ Report a syntax error at a location. """
        
        print(f"[line {line}] Error{where}: {message}")
        self.error_count += 1
    
    
    def had_error(self: Self) -> bool:
        """ Return whether a syntax error has been reported. """
        
        return self.error_count > 0
    
    
    def clear(self: Self) -> None:
        """ Clear any reported syntax errors. """
        
        self.error_count = 0
