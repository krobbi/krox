from krox_token import Token
from typing import Any, Self

class Expr:
    """ An expression in a tree. """
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        pass


class AssignExpr(Expr):
    """ An assign expression in a tree. """
    
    name: Token
    """ The assign expression's name. """
    
    value: Expr
    """ The assign expression's value. """
    
    def __init__(self: Self, name: Token, value: Expr) -> None:
        """ Initialize the assign expression's name and value. """
        
        super().__init__()
        self.name = name
        self.value = value
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_assign_expr(self)


class BinaryExpr(Expr):
    """ A binary expression in a tree. """
    
    left: Expr
    """ The binary expression's left operand. """
    
    operator: Token
    """ The binary expression's operator. """
    
    right: Expr
    """ The binrary expression's right operand. """
    
    def __init__(self: Self, left: Expr, operator: Token, right: Expr) -> None:
        """
        Initialize the binary expression's operator and operands.
        """
        
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_binary_expr(self)


class GroupingExpr(Expr):
    """ A grouping expression in a tree. """
    
    expression: Expr
    """ The grouping expression's expression. """
    
    def __init__(self: Self, expression: Expr) -> None:
        """ Initialize the grouping expression's expression. """
        
        super().__init__()
        self.expression = expression
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_grouping_expr(self)


class LiteralExpr(Expr):
    """ A literal expression in a tree. """
    
    value: Any
    """ The literal expression's value. """
    
    def __init__(self: Self, value: Any) -> None:
        """ Initialize the literal expression's value. """
        
        super().__init__()
        self.value = value
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_literal_expr(self)


class UnaryExpr(Expr):
    """ A unary expression in a tree. """
    
    operator: Token
    """ The unary expression's operator. """
    
    right: Expr
    """ The unary expression's right operand. """
    
    def __init__(self: Self, operator: Token, right: Expr) -> None:
        """ Initialize the unary expression's operator and operand. """
        
        super().__init__()
        self.operator = operator
        self.right = right
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_unary_expr(self)


class VariableExpr(Expr):
    """ A variable expression in a tree. """
    
    name: Token
    """ The variable expression's name. """
    
    def __init__(self: Self, name: Token) -> None:
        """ Initialize the variable expression's name. """
        
        super().__init__()
        self.name = name
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_variable_expr(self)


class ExprVisitor:
    """ Visits expressions. """
    
    def visit_assign_expr(self: Self, expr: AssignExpr) -> Any:
        """ Visit an assign expression. """
        
        pass
    
    
    def visit_binary_expr(self: Self, expr: BinaryExpr) -> Any:
        """ Visit a binary expression. """
        
        pass
    
    
    def visit_grouping_expr(self: Self, expr: GroupingExpr) -> Any:
        """ Visit a grouping expression. """
        
        pass
    
    
    def visit_literal_expr(self: Self, expr: LiteralExpr) -> Any:
        """ Visit a literal expression. """
        
        pass
    
    
    def visit_unary_expr(self: Self, expr: UnaryExpr) -> Any:
        """ Visit a unary expression. """
        
        pass
    
    
    def visit_variable_expr(self: Self, expr: VariableExpr) -> Any:
        """ Visit a variable expression. """
        
        pass
