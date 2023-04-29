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


class FunctionStmt(Stmt):
    """ A function statement in a tree. """
    
    name: Token
    """ The function's name. """
    
    params: list[Token]
    """ The function's parameters. """
    
    body: list[Stmt]
    """ The function's body. """
    
    def __init__(
            self: Self,
            name: Token, params: list[Token], body: list[Stmt]) -> None:
        """
        Initialize the function statement's name, parameters and body.
        """
        
        super().__init__()
        self.name = name
        self.params = params
        self.body = body
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept a statement visitor. """
        
        return visitor.visit_function_stmt(self)


class IfStmt(Stmt):
    """ An if statement in a tree. """
    
    condition: Expr
    """ The if statement's condition. """
    
    then_branch: Stmt
    """ The if statement's then branch. """
    
    else_branch: Stmt | None
    """ The if statement's else branch. """
    
    def __init__(
            self: Self, condition: Expr,
            then_branch: Stmt, else_branch: Stmt | None) -> None:
        """ Initialize the if statement's condition and branches. """
        
        super().__init__()
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept a statement visitor. """
        
        return visitor.visit_if_stmt(self)


class ReturnStmt(Stmt):
    """ A return statement in a tree. """
    
    keyword: Token
    """ The return statement's keyword for error logging. """
    
    value: Expr | None
    """ The return statement's value. """
    
    def __init__(self: Self, keyword: Token, value: Expr | None) -> None:
        """ Initialize the return statement's keyword and value. """
        
        super().__init__()
        self.keyword = keyword
        self.value = value
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept a statement visitor. """
        
        return visitor.visit_return_stmt(self)


class VarStmt(Stmt):
    """ A var statement in a tree. """
    
    name: Token
    """ The var statement's name. """
    
    initializer: Expr | None
    """ The var statement's initializer. """
    
    def __init__(self: Self, name: Token, initializer: Expr | None) -> None:
        """ Initialize the var statement's name and initializer. """
        
        super().__init__()
        self.name = name
        self.initializer = initializer
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept a statement visitor. """
        
        return visitor.visit_var_stmt(self)


class WhileStmt(Stmt):
    """ A while statement in a tree. """
    
    condition: Expr
    """ The while statement's condition. """
    
    body: Stmt
    """ The while statement's body. """
    
    def __init__(self: Self, condition: Expr, body: Stmt) -> None:
        """ Initialize the while statement's condition and body. """
        
        super().__init__()
        self.condition = condition
        self.body = body
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept a statement visitor. """
        
        return visitor.visit_while_stmt(self)


class StmtVisitor:
    """ Visits statements. """
    
    def visit_block_stmt(self: Self, stmt: BlockStmt) -> Any:
        """ Visit a block statement. """
        
        pass
    
    
    def visit_expression_stmt(self: Self, stmt: ExpressionStmt) -> Any:
        """ Visit an expression statement. """
        
        pass
    
    
    def visit_function_stmt(self: Self, stmt: FunctionStmt) -> Any:
        """ Visit a function statement. """
        
        pass
    
    
    def visit_if_stmt(self: Self, stmt: IfStmt) -> Any:
        """ Visit an if statement. """
        
        pass
    
    
    def visit_return_stmt(self: Self, stmt: ReturnStmt) -> Any:
        """ Visit a return statement. """
        
        pass
    
    
    def visit_var_stmt(self: Self, stmt: VarStmt) -> Any:
        """ Visit a var statement. """
        
        pass
    
    
    def visit_while_stmt(self: Self, stmt: WhileStmt) -> Any:
        """ Visit a while statement. """
        
        pass
