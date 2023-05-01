from enum import Enum, auto
from krox_error_reporter import ErrorReporter
from krox_expr import AssignExpr, BinaryExpr, CallExpr, Expr, ExprVisitor
from krox_expr import GetExpr, GroupingExpr, LiteralExpr, LogicalExpr, SetExpr
from krox_expr import ThisExpr, UnaryExpr, VariableExpr
from krox_interpreter import Interpreter
from krox_stmt import BlockStmt, ClassStmt, ExpressionStmt, FunctionStmt
from krox_stmt import IfStmt, ReturnStmt, Stmt, StmtVisitor, VarStmt, WhileStmt
from krox_token import Token
from typing import Self

class FunctionType(Enum):
    """ The type of a function. """
    
    NONE = auto()
    """ Not a function. """
    
    FUNCTION = auto()
    """ Function. """
    
    INITIALIZER = auto()
    """ Instance constructor. """
    
    METHOD = auto()
    """ Instance method. """


class ClassType(Enum):
    """ The type of a class. """
    
    NONE = auto()
    """ Not a class. """
    
    CLASS = auto()
    """ Class. """


class Resolver(StmtVisitor, ExprVisitor):
    """ Resolves variable in an AST before it is interpreted. """
    
    error_reporter: ErrorReporter
    """ The resolver's error reporter. """
    
    interpreter: Interpreter
    """ The resolver's interpreter. """
    
    scopes: list[dict[str, bool]]
    """ The resolver's stack of local scopes. """
    
    current_function: FunctionType
    """ The resolver's current function type. """
    
    current_class: ClassType
    """ The resolver's current class type. """
    
    def __init__(
            self: Self,
            error_reporter: ErrorReporter, interpreter: Interpreter) -> None:
        """ Initialize the resolver. """
        
        super().__init__()
        self.error_reporter = error_reporter
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE
    
    
    def resolve(self: Self, node: list[Stmt] | Stmt | Expr) -> None:
        """ Resolve an AST node. """
        
        if isinstance(node, list):
            for statement in node:
                statement.accept(self)
        else:
            node.accept(self)
    
    
    def resolve_function(
            self: Self, function: FunctionStmt, type: FunctionType) -> None:
        """ Resolve a function statement. """
        
        enclosing_function: FunctionType = self.current_function
        self.current_function = type
        self.begin_scope()
        
        for param in function.params:
            self.declare(param)
            self.define(param)
        
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function
    
    
    def begin_scope(self: Self) -> None:
        """ Begin a new scope. """
        
        self.scopes.append({})
    
    
    def end_scope(self: Self) -> None:
        """ End the current scope. """
        
        self.scopes.pop()
    
    
    def declare(self: Self, name: Token) -> None:
        """ Declare a name in the current scope. """
        
        if not self.scopes:
            return
        
        if name.lexeme in self.scopes[-1]:
            self.error_reporter.error(
                    name, "Already a variable with this name in this scope.")
        
        self.scopes[-1][name.lexeme] = False
    
    
    def define(self: Self, name: Token) -> None:
        """ Define a name in the current scope. """
        
        if not self.scopes:
            return
        
        self.scopes[-1][name.lexeme] = True
    
    
    def resolve_local(self: Self, expr: Expr, name: Token) -> None:
        """ Resolve a local variable to an expression. """
        
        for index in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[index]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - index)
                return
    
    
    def visit_block_stmt(self: Self, stmt: BlockStmt) -> None:
        """ Visit and resolve a block statement. """
        
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
    
    
    def visit_class_stmt(self: Self, stmt: ClassStmt) -> None:
        """ Visit and resolve a class statement. """
        
        enclosing_class: ClassType = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        
        self.begin_scope()
        self.scopes[-1]["this"] = True
        
        for method in stmt.methods:
            declaration: FunctionType = FunctionType.METHOD
            
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            
            self.resolve_function(method, declaration)
        
        self.end_scope()
        self.current_class = enclosing_class
    
    
    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        """ Visit and resolve an expression statement. """
        
        self.resolve(stmt.expression)
    
    
    def visit_function_stmt(self: Self, stmt: FunctionStmt) -> None:
        """ Visit and resolve a function statement. """
        
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)
    
    
    def visit_if_stmt(self: Self, stmt: IfStmt) -> None:
        """ Visit and resolve an if statement. """
        
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)
    
    
    def visit_return_stmt(self: Self, stmt: ReturnStmt) -> None:
        """ Visit and resolve a return statement. """
        
        if self.current_function == FunctionType.NONE:
            self.error_reporter.error(
                    stmt.keyword, "Can't return from top level code.")
        
        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                self.error_reporter.error(
                        stmt.keyword,
                        "Can't return a value from an initializer.")
            
            self.resolve(stmt.value)
    
    
    def visit_var_stmt(self: Self, stmt: VarStmt) -> None:
        """ Visit and resolve a var statement. """
        
        self.declare(stmt.name)
        
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        
        self.define(stmt.name)
    
    
    def visit_while_stmt(self: Self, stmt: WhileStmt) -> None:
        """ Visit and resolve a while statement. """
        
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
    
    
    def visit_assign_expr(self: Self, expr: AssignExpr) -> None:
        """ Visit and resolve an assign expression. """
        
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
    
    
    def visit_binary_expr(self: Self, expr: BinaryExpr) -> None:
        """ Visit and resolve a binary expression. """
        
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    
    def visit_call_expr(self: Self, expr: CallExpr) -> None:
        """ Visit and resolve a call expression. """
        
        self.resolve(expr.callee)
        
        for argument in expr.arguments:
            self.resolve(argument)
    
    
    def visit_get_expr(self: Self, expr: GetExpr) -> None:
        """ Visit and resolve a get expression. """
        
        self.resolve(expr.object)
    
    
    def visit_grouping_expr(self: Self, expr: GroupingExpr) -> None:
        """ Visit and resolve a grouping expression. """
        
        self.resolve(expr.expression)
    
    
    def visit_literal_expr(self: Self, expr: LiteralExpr) -> None:
        """ Visit and resolve a literal expression. """
        
        pass
    
    
    def visit_logical_expr(self: Self, expr: LogicalExpr) -> None:
        """ Visit and resolve a logical expression. """
        
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    
    def visit_set_expr(self: Self, expr: SetExpr) -> None:
        """ Visit and resolve a set expression. """
        
        self.resolve(expr.value)
        self.resolve(expr.object)
    
    
    def visit_this_expr(self: Self, expr: ThisExpr) -> None:
        """ Visit and resole a this expression. """
        
        if self.current_class == ClassType.NONE:
            self.error_reporter.error(
                    expr.keyword, "Can't use `this` outside of a class.")
        
        self.resolve_local(expr, expr.keyword)
    
    
    def visit_unary_expr(self: Self, expr: UnaryExpr) -> None:
        """ Visit and resolve a unary expression. """
        
        self.resolve(expr.right)
    
    
    def visit_variable_expr(self: Self, expr: VariableExpr) -> None:
        """ Visit and resolve a variable expression. """
        
        if self.scopes and not self.scopes[-1].get(expr.name.lexeme, True):
            self.error_reporter.error(
                    expr.name,
                    "Can't read local variable in its own initializer.")
        
        self.resolve_local(expr, expr.name)
