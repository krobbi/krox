from lox_token_type import TokenType
from typing import Any, Self

class Token:
    """ A token generated by the scanner. """
    
    type: TokenType
    """ The type of the token. """
    
    lexeme: str
    """ The source code that generated the token. """
    
    literal: Any
    """ The token's value. """
    
    line: int
    """ The line number that the token was generated from. """
    
    def __init__(
            self: Self,
            type: TokenType, lexeme: str, literal: Any, line: int) -> None:
        """ Initialize the token. """
        
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    
    def __repr__(self: Self) -> str:
        """ Represent the token as a string. """
        
        return f"{self.type} {self.lexeme} {self.literal}"
