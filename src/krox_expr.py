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


class CallExpr(Expr):
    """ A call expression in a tree. """
    
    callee: Expr
    """ The call expression's callee. """
    
    paren: Token
    """ The call expression's closing parenthesis for error logging. """
    
    arguments: list[Expr]
    """ The call expression's arguments. """
    
    def __init__(
            self: Self,
            callee: Expr, paren: Token, arguments: list[Expr]) -> None:
        """
        Initialize the call expression's callee, closing parenthesis,
        and arguments.
        """
        
        super().__init__()
        self.callee = callee
        self.paren = paren
        self.arguments = arguments
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_call_expr(self)


class GetExpr(Expr):
    """ A get expression in a tree. """
    
    object: Expr
    """ The get expression's object. """
    
    name: Token
    """ The get expression's token. """
    
    def __init__(self: Self, object: Expr, name: Token) -> None:
        """ Initialize the get expression's object and name. """
        
        super().__init__()
        self.object = object
        self.name = name
    
    
    def accept(self: Self, visitor: Any) -> None:
        """ Accept an expression visitor. """
        
        return visitor.visit_get_expr(self)


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


class LogicalExpr(Expr):
    """ A logical expression in a tree. """
    
    left: Expr
    """ The logical expression's left operand. """
    
    operator: Token
    """ The logical expression's operator. """
    
    right: Expr
    """ The logical expression's right operand. """
    
    def __init__(self: Self, left: Expr, operator: Token, right: Expr) -> None:
        """ Initialize the logical expression's operator and operands. """
        
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_logical_expr(self)


class SetExpr(Expr):
    """ A set expression in a tree. """
    
    object: Expr
    """ The set expression's object. """
    
    name: Token
    """ The set expression's name. """
    
    value: Expr
    """ The set expression's value. """
    
    def __init__(self: Self, object: Expr, name: Token, value: Expr) -> None:
        """ Initialize the set expression's object, name, and value. """
        
        super().__init__()
        self.object = object
        self.name = name
        self.value = value
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_set_expr(self)


class SuperExpr(Expr):
    """ A super expression in a tree. """
    
    keyword: Token
    """ The super expression's keyword. """
    
    method: Token
    """ The super expression's method. """
    
    def __init__(self: Self, keyword: Token, method: Token) -> None:
        """ Initialize the super expression's keyword and method. """
        
        super().__init__()
        self.keyword = keyword
        self.method = method
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_super_expr(self)


class ThisExpr(Expr):
    """ A this expression in a tree. """
    
    keyword: Token
    """ The this expression's keyword. """
    
    def __init__(self: Self, keyword: Token) -> None:
        """ Initialize the this expression's keyword. """
        
        super().__init__()
        self.keyword = keyword
    
    
    def accept(self: Self, visitor: Any) -> Any:
        """ Accept an expression visitor. """
        
        return visitor.visit_this_expr(self)


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
    
    
    def visit_call_expr(self: Self, expr: CallExpr) -> Any:
        """ Visit a call expression. """
        
        pass
    
    
    def visit_get_expr(self: Self, expr: GetExpr) -> Any:
        """ Visit a get expression. """
        
        pass
    
    
    def visit_grouping_expr(self: Self, expr: GroupingExpr) -> Any:
        """ Visit a grouping expression. """
        
        pass
    
    
    def visit_literal_expr(self: Self, expr: LiteralExpr) -> Any:
        """ Visit a literal expression. """
        
        pass
    
    
    def visit_logical_expr(self: Self, expr: LogicalExpr) -> Any:
        """ Visit a logical expression. """
        
        pass
    
    
    def visit_set_expr(self: Self, expr: SetExpr) -> Any:
        """ Visit a set expression. """
        
        pass
    
    
    def visit_super_expr(self: Self, expr: SuperExpr) -> Any:
        """ Visit a super expression. """
        
        pass
    
    
    def visit_this_expr(self: Self, expr: ThisExpr) -> Any:
        """ Visit a this expression. """
        
        pass
    
    
    def visit_unary_expr(self: Self, expr: UnaryExpr) -> Any:
        """ Visit a unary expression. """
        
        pass
    
    
    def visit_variable_expr(self: Self, expr: VariableExpr) -> Any:
        """ Visit a variable expression. """
        
        pass
