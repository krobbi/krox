from enum import Enum, auto

class TokenType(Enum):
    """ The type of a token. """
    
    LEFT_PAREN = auto()
    """ `(`. """
    
    RIGHT_PAREN = auto()
    """ `)`. """
    
    LEFT_BRACE = auto()
    """ `{`. """
    
    RIGHT_BRACE = auto()
    """ `}`. """
    
    COMMA = auto()
    """ `,`. """
    
    DOT = auto()
    """ `.`. """
    
    MINUS = auto()
    """ `-`. """
    
    PLUS = auto()
    """ `+`. """
    
    SEMICOLON = auto()
    """ `;`. """
    
    SLASH = auto()
    """ `/`. """
    
    STAR = auto()
    """ `*`. """
    
    BANG = auto()
    """ `!`. """
    
    BANG_EQUAL = auto()
    """ `!=`. """
    
    EQUAL = auto()
    """ `=`. """
    
    EQUAL_EQUAL = auto()
    """ `==`. """
    
    GREATER = auto()
    """ `>`. """
    
    GREATER_EQUAL = auto()
    """ `>=`. """
    
    LESS = auto()
    """ `<`. """
    
    LESS_EQUAL = auto()
    """ `<=`. """
    
    IDENTIFIER = auto()
    """ Identifier literal. """
    
    STRING = auto()
    """ String literal. """
    
    NUMBER = auto()
    """ Number literal. """
    
    AND = auto()
    """ `and`. """
    
    CLASS = auto()
    """ `class`. """
    
    ELSE = auto()
    """ `else`. """
    
    FALSE = auto()
    """ `false`. """
    
    FUN = auto()
    """ `fun`. """
    
    FOR = auto()
    """ `for`. """
    
    IF = auto()
    """ `if`. """
    
    NIL = auto()
    """ `nil`. """
    
    OR = auto()
    """ `or`. """
    
    RETURN = auto()
    """ `return`. """
    
    SUPER = auto()
    """ `super`. """
    
    THIS = auto()
    """ `this`. """
    
    TRUE = auto()
    """ `true`. """
    
    VAR = auto()
    """ `var`. """
    
    WHILE = auto()
    """ `while`. """
    
    EOF = auto()
    """ End of file marker. """
