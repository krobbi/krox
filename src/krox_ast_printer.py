from krox_expr import BinaryExpr, Expr, ExprVisitor, GroupingExpr, LiteralExpr
from krox_expr import UnaryExpr
from typing import Self

class ASTPrinter(ExprVisitor):
    """ Creates an unambiguous string from an expression tree. """
    
    def print(self: Self, expr: Expr) -> str:
        """ Represent an expression tree as an unambiguous string. """
        
        return expr.accept(self)
    
    
    def visit_binary_expr(self: Self, expr: BinaryExpr) -> str:
        """ Visit a binary expression and return a string. """
        
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    
    def visit_grouping_expr(self: Self, expr: GroupingExpr) -> str:
        """ Visit a grouping expression and return a string. """
        
        return self.parenthesize("group", expr.expression)
    
    
    def visit_literal_expr(self: Self, expr: LiteralExpr) -> str:
        """ Visit a literal expression and return a string. """
        
        if expr.value is None:
            return "nil"
        
        return str(expr.value)
    
    
    def visit_unary_expr(self: Self, expr: UnaryExpr) -> str:
        """ Visit a unary expression and return a string. """
        
        return self.parenthesize(expr.operator.lexeme, expr.right)
    
    
    def parenthesize(self: Self, name: str, *exprs: Expr) -> str:
        """ Parenthesize a name and expressions to a string. """
        
        result: str = f"({name}"
        
        for expr in exprs:
            result = f"{result} {expr.accept(self)}"
        
        return f"{result})"
