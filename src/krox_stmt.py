from krox_expr import Expr
from krox_token import Token
from typing import Any, Self

class Stmt:
    """ A statement in a tree. """
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept a statement visitor. """
        
        pass


class BlockStmt(Stmt):
    """ A block statement in a tree. """
    
    statements: list[Stmt]
    """ The block statement's statements. """
    
    def __init__(self: Self, statements: list[Stmt]) -> None:
        """ Initialize the block statement's statements. """
        
        super().__init__()
        self.statements = statements
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept a statement visitor. """
        
        return visitor.visit_block_stmt(self)


class ExpressionStmt(Stmt):
    """ An expression statement in a tree. """
    
    expression: Expr
    """ The expression statement's expression. """
    
    def __init__(self: Self, expression: Expr) -> None:
        """ Initialize the expression statement's expression. """
        
        super().__init__()
        self.expression = expression
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept a statement visitor. """
        
        return visitor.visit_expression_stmt(self)


class PrintStmt(Stmt):
    """ A print statement in a tree. """
    
    expression: Expr
    """ The print statement's expression. """
    
    def __init__(self: Self, expression: Expr) -> None:
        """ Initialize the print statement's expression. """
        
        super().__init__()
        self.expression = expression
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept a statement visitor. """
        
        return visitor.visit_print_stmt(self)


class VarStmt(Stmt):
    """ A var statement in a tree. """
    
    name: Token
    """ The var statement's name. """
    
    initializer: Expr
    """ The var statement's initializer. """
    
    def __init__(self: Self, name: Token, initializer: Expr) -> None:
        """ Initialize the var statement's name and initializer. """
        
        super().__init__()
        self.name = name
        self.initializer = initializer
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept a statement visitor. """
        
        return visitor.visit_var_stmt(self)


class StmtVisitor:
    """ Visits statements. """
    
    def visit_block_stmt(self: Self, stmt: BlockStmt) -> Any:
        """ Visit a block statement. """
        
        pass
    
    
    def visit_expression_stmt(self: Self, stmt: ExpressionStmt) -> Any:
        """ Visit an expression statement. """
        
        pass
    
    
    def visit_print_stmt(self: Self, stmt: PrintStmt) -> Any:
        """ Visit a print statement. """
        
        pass
    
    
    def visit_var_stmt(self: Self, stmt: VarStmt) -> Any:
        """ Visit a var statement. """
        
        pass
