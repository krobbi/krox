from krox_expr import BinaryExpr, Expr, ExprVisitor, GroupingExpr, LiteralExpr
from krox_expr import UnaryExpr
from typing import Self

class PrinterNode:
    """ Contains a name and child printer nodes. """
    
    name: str
    children: tuple[Self]
    
    def __init__(self: Self, name: str, *children: Self) -> None:
        """ Initialize the printer node's name and children. """
        
        self.name = name
        self.children = children
    
    
    def __repr__(self: Self) -> str:
        """ Represent the printer node as a string. """
        
        return self.print([])
    
    
    def print(self: Self, indent_flags: list[bool]) -> str:
        """
        Represent the printer node as a string from indent flags.
        """
        
        result: str = ""
        
        for index, is_connected in enumerate(indent_flags):
            if index == len(indent_flags) - 1:
                result = f"{result}{'├' if is_connected else '╰'}───"
            else:
                result = f"{result}{'│' if is_connected else ' '}   "
        
        result = f"{result}[{self.name}]"
        
        for index, child in enumerate(self.children):
            indent_flags.append(index != len(self.children) - 1)
            result = f"{result}\n{child.print(indent_flags)}"
            indent_flags.pop()
        
        return result


class ASTPrinter(ExprVisitor):
    """ Creates an unambiguous string from an expression tree. """
    
    def print(self: Self, expr: Expr) -> str:
        """ Represent an expression tree as a string. """
        
        return str(expr.accept(self))
    
    
    def visit_binary_expr(self: Self, expr: BinaryExpr) -> PrinterNode:
        """ Visit a binary expression and return a printer node. """
        
        return PrinterNode(
                expr.operator.lexeme,
                expr.left.accept(self), expr.right.accept(self))
    
    
    def visit_grouping_expr(self: Self, expr: GroupingExpr) -> PrinterNode:
        """ Visit a grouping expression and return a printer node. """
        
        return PrinterNode("()", expr.expression.accept(self))
    
    
    def visit_literal_expr(self: Self, expr: LiteralExpr) -> PrinterNode:
        """ Visit a literal expression and return a printer node. """
        
        if expr.value is True:
            return PrinterNode("true")
        
        if expr.value is False:
            return PrinterNode("false")
        
        if expr.value is None:
            return PrinterNode("nil")
        
        if isinstance(expr.value, str):
            return PrinterNode(f'"{expr.value}"')
        
        return PrinterNode(str(expr.value))
    
    
    def visit_unary_expr(self: Self, expr: UnaryExpr) -> PrinterNode:
        """ Visit a unary expression and return a printer node. """
        
        return PrinterNode(expr.operator.lexeme, expr.right.accept(self))
