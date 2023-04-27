from krox_error_reporter import ErrorReporter
from krox_expr import BinaryExpr, Expr, ExprVisitor, GroupingExpr, LiteralExpr
from krox_expr import UnaryExpr
from krox_token import Token
from krox_token_type import TokenType
from typing import Any, Self

class Interpreter(ExprVisitor):
    """ Interprets an expression tree. """
    
    error_reporter: ErrorReporter
    """ The interpreter's error reporter. """
    
    def __init__(self: Self, error_reporter: ErrorReporter) -> None:
        """ Initialize the interpreter. """
        
        super().__init__()
        self.error_reporter = error_reporter
    
    
    def interpret(self: Self, expr: Expr) -> None:
        """ Interpret an expression. """
        
        try:
            value: Any = self.evaluate(expr)
            print(self.to_string(value))
        except RuntimeError:
            pass
    
    
    def evaluate(self: Self, expr: Expr) -> Any:
        """ Evaluate an expression as a value. """
        
        return expr.accept(self)
    
    
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
    
    
    def to_string(self: Self, value: Any) -> str:
        """ Represent a value as a Krox string. """
        
        if value is True:
            return "true"
        
        if value is False:
            return "false"
        
        if value is None:
            return "nil"
        
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
