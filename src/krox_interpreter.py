from krox_environment import Environment
from krox_error_reporter import ErrorReporter
from krox_expr import AssignExpr, BinaryExpr, Expr, ExprVisitor, GroupingExpr
from krox_expr import LiteralExpr, UnaryExpr, VariableExpr
from krox_stmt import BlockStmt, ExpressionStmt, PrintStmt, Stmt, StmtVisitor
from krox_stmt import VarStmt
from krox_token import Token
from krox_token_type import TokenType
from typing import Any, Self

class Interpreter(StmtVisitor, ExprVisitor):
    """ Interprets a list of statements. """
    
    error_reporter: ErrorReporter
    """ The interpreter's error reporter. """
    
    environment: Environment
    """ The interpreter's environment. """
    
    def __init__(self: Self, error_reporter: ErrorReporter) -> None:
        """ Initialize the interpreter. """
        
        super().__init__()
        self.error_reporter = error_reporter
        self.environment = Environment(error_reporter)
    
    
    def interpret(self: Self, statements: list[Stmt]) -> None:
        """ Interpret a list of statements. """
        
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError:
            pass
    
    
    def evaluate(self: Self, expr: Expr) -> Any:
        """ Evaluate an expression as a value. """
        
        return expr.accept(self)
    
    
    def execute(self: Self, stmt: Stmt) -> None:
        """ Execute a statement. """
        
        stmt.accept(self)
    
    
    def execute_block(
            self: Self,
            statements: list[Stmt], environment: Environment) -> None:
        """ Execute a block of statements in a new environment. """
        
        previous: Environment = self.environment
        
        try:
            self.environment = environment
            
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    
    def visit_block_stmt(self: Self, stmt: BlockStmt) -> None:
        """ Visit and execute a block statement. """
        
        self.execute_block(
                stmt.statements,
                Environment(self.error_reporter, self.environment))
    
    
    def visit_expression_stmt(self: Self, stmt: ExpressionStmt) -> None:
        """ Visit and execute an expression statement. """
        
        self.evaluate(stmt.expression)
    
    
    def visit_print_stmt(self: Self, stmt: PrintStmt) -> None:
        """ Visit and execute a print statement. """
        
        value: Any = self.evaluate(stmt.expression)
        print(self.stringify(value))
    
    
    def visit_var_stmt(self: Self, stmt: VarStmt) -> None:
        """ Visit and execute a var statement. """
        
        value: Any = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
    
    
    def visit_assign_expr(self: Self, expr: AssignExpr) -> Any:
        """ Visit an assign expression and return a value. """
        
        value: Any = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value
    
    
    def visit_binary_expr(self: Self, expr: BinaryExpr) -> Any:
        """ Visit a binary expression and return a value. """
        
        left: Any = self.evaluate(expr.left)
        right: Any = self.evaluate(expr.right)
        
        match expr.operator.type:
            case TokenType.GREATER:
                self.check_number_operands(left, expr.operator, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(left, expr.operator, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.check_number_operands(left, expr.operator, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(left, expr.operator, right)
                return float(left) <= float(right)
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case TokenType.MINUS:
                self.check_number_operands(left, expr.operator, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                
                raise self.error(
                        expr.operator,
                        "Operands must both be numbers or strings.")
            case TokenType.SLASH:
                self.check_number_operands(left, expr.operator, right)
                
                if right == 0.0:
                    raise self.error(expr.operator, "Cannot divide by zero.")
                
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(left, expr.operator, right)
                return float(left) * float(right)
        
        raise self.error(expr.operator, "Unimplemented binary operator.")
    
    
    def visit_grouping_expr(self: Self, expr: GroupingExpr) -> Any:
        """ Visit a grouping expression and return a value. """
        
        return self.evaluate(expr.expression)
    
    
    def visit_literal_expr(self: Self, expr: LiteralExpr) -> Any:
        """ Visit a literal expression and return a value. """
        
        return expr.value
    
    
    def visit_unary_expr(self: Self, expr: UnaryExpr) -> Any:
        """ Visit a unary expression and return a value. """
        
        right: Any = self.evaluate(expr.right)
        
        match expr.operator.type:
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not self.is_truthy(right)
        
        raise self.error(expr.operator, "Unimplemented unary operator.")
    
    
    def visit_variable_expr(self: Self, expr: VariableExpr) -> Any:
        """ Visit a variable expression and return a value. """
        
        return self.environment.get(expr.name)
    
    
    def is_truthy(self: Self, value: Any) -> bool:
        """ Return whether a value is truthy in Krox. """
        
        if value is None:
            return False
        
        if isinstance(value, bool):
            return bool(value)
        
        return True
    
    
    def is_equal(self: Self, a: Any, b: Any) -> bool:
        """ Return whether two values are equal in Krox. """
        
        if type(a) != type(b):
            return False
        
        return a == b
    
    
    def stringify(self: Self, value: Any) -> str:
        """ Convert a Krox value to a string. """
        
        if value is True:
            return "true"
        
        if value is False:
            return "false"
        
        if value is None:
            return "nil"
        
        if isinstance(value, float):
            text: str = str(value)
            
            if text == "-0.0":
                return "0"
            
            if text.endswith(".0"):
                return text[:-2]
            
            return text
        
        return str(value)
    
    
    def check_number_operand(self: Self, operator: Token, right: Any) -> None:
        """
        Throw an error if a unary operator token's operand is not a
        number.
        """
        
        if not isinstance(right, float):
            raise self.error(operator, "Operand must be a number.")
    
    
    def check_number_operands(
            self: Self, left: Any, operator: Token, right: Any) -> None:
        """
        Throw an error if a either of a binary operator token's operands
        are not numbers.
        """
        
        if not isinstance(left, float) or not isinstance(right, float):
            raise self.error(operator, "Operands must both be numbers.")
    
    
    def error(self: Self, token: Token, message: str) -> RuntimeError:
        """
        Report an error from a token and a message and return a runtime
        error.
        """
        
        self.error_reporter.error(token, message)
        return RuntimeError()
