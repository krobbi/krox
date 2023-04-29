from krox_expr import AssignExpr, BinaryExpr, ExprVisitor, GroupingExpr
from krox_expr import LiteralExpr, LogicalExpr, UnaryExpr, VariableExpr
from krox_stmt import BlockStmt, ExpressionStmt, IfStmt, PrintStmt, Stmt
from krox_stmt import StmtVisitor, VarStmt, WhileStmt
from typing import Any, Self

class PrinterNode:
    """ Contains a name and child printer nodes. """
    
    name: str
    children: list[Self]
    
    def __init__(self: Self, name: str, *children: Self) -> None:
        """ Initialize the printer node's name and children. """
        
        self.name = name
        self.children = list(children)
    
    
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
        
        result = f"{result}{self.name}"
        
        for index, child in enumerate(self.children):
            indent_flags.append(index != len(self.children) - 1)
            result = f"{result}\n{child.print(indent_flags)}"
            indent_flags.pop()
        
        return result


class ASTPrinter(StmtVisitor, ExprVisitor):
    """ Creates an unambiguous string from a statement tree. """
    
    def print(self: Self, statement: Stmt) -> str:
        """ Represent an statement tree as a string. """
        
        return str(statement.accept(self))
    
    
    def visit_block_stmt(self: Self, stmt: BlockStmt) -> PrinterNode:
        """ Visit a block statement and return a printer node. """
        
        node: PrinterNode = PrinterNode("{}")
        
        for statement in stmt.statements:
            node.children.append(statement.accept(self))
        
        return node
    
    
    def visit_expression_stmt(self: Self, stmt: ExpressionStmt) -> PrinterNode:
        """ Visit an expression statement and return a printer node. """
        
        return PrinterNode("{expression}", stmt.expression.accept(self))
    
    
    def visit_if_stmt(self: Self, stmt: IfStmt) -> PrinterNode:
        """ Visit an if statement and return a printer node. """
        
        node: PrinterNode = PrinterNode(
                "{if}",
                stmt.condition.accept(self), stmt.then_branch.accept(self))
        
        if stmt.else_branch is not None:
            node.children.append(stmt.else_branch.accept(self))
        
        return node
    
    
    def visit_print_stmt(self: Self, stmt: PrintStmt) -> PrinterNode:
        """ Visit a print statement and return a printer node. """
        
        return PrinterNode("{print}", stmt.expression.accept(self))
    
    
    def visit_var_stmt(self: Self, stmt: VarStmt) -> PrinterNode:
        """ Visit a var statement and return a printer node. """
        
        node: PrinterNode = PrinterNode(f"{{var {stmt.name.lexeme}}}")
        
        if stmt.initializer is not None:
            node.children.append(stmt.initializer.accept(self))
        
        return node
    
    
    def visit_while_stmt(self: Self, stmt: WhileStmt) -> PrinterNode:
        """ Visit a while statement and return a printer node. """
        
        return PrinterNode(
                "{while}", stmt.condition.accept(self), stmt.body.accept(self))
    
    
    def visit_assign_expr(self: Self, expr: AssignExpr) -> PrinterNode:
        """ Visit an assign expression and return a printer node. """
        
        return PrinterNode(f"({expr.name.lexeme} =)", expr.value.accept(self))
    
    
    def visit_binary_expr(self: Self, expr: BinaryExpr) -> PrinterNode:
        """ Visit a binary expression and return a printer node. """
        
        return PrinterNode(
                f"({expr.operator.lexeme})",
                expr.left.accept(self), expr.right.accept(self))
    
    
    def visit_grouping_expr(self: Self, expr: GroupingExpr) -> PrinterNode:
        """ Visit a grouping expression and return a printer node. """
        
        return PrinterNode("()", expr.expression.accept(self))
    
    
    def visit_literal_expr(self: Self, expr: LiteralExpr) -> PrinterNode:
        """ Visit a literal expression and return a printer node. """
        
        if expr.value is True:
            return PrinterNode("(true)")
        
        if expr.value is False:
            return PrinterNode("(false)")
        
        if expr.value is None:
            return PrinterNode("(nil)")
        
        if isinstance(expr.value, str):
            return PrinterNode(f'("{expr.value}")')
        
        return PrinterNode(f"({expr.value})")
    
    
    def visit_logical_expr(self: Self, expr: LogicalExpr) -> PrinterNode:
        """ Visit a logical expression and return a printer node. """
        
        return PrinterNode(
                f"({expr.operator.lexeme})",
                expr.left.accept(self), expr.right.accept(self))
    
    
    def visit_unary_expr(self: Self, expr: UnaryExpr) -> PrinterNode:
        """ Visit a unary expression and return a printer node. """
        
        return PrinterNode(expr.operator.lexeme, expr.right.accept(self))
    
    
    def visit_variable_expr(self: Self, expr: VariableExpr) -> PrinterNode:
        """ Visit a variable expression and return a printer node. """
        
        return PrinterNode(f"({expr.name.lexeme})")
