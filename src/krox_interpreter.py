from krox_callable import KroxCallable
from krox_class import KroxClass
from krox_environment import Environment
from krox_error_reporter import ErrorReporter
from krox_expr import AssignExpr, BinaryExpr, CallExpr, Expr, ExprVisitor
from krox_expr import GetExpr, GroupingExpr, LiteralExpr, LogicalExpr, SetExpr
from krox_expr import ThisExpr, UnaryExpr, VariableExpr
from krox_function import ReturnException, KroxFunction
from krox_instance import KroxInstance
from krox_native_function import ClockNativeFunction, PrintNativeFunction
from krox_stmt import BlockStmt, ClassStmt, ExpressionStmt, FunctionStmt
from krox_stmt import IfStmt, ReturnStmt, Stmt, StmtVisitor, VarStmt, WhileStmt
from krox_token import Token
from krox_token_type import TokenType
from typing import Any, Self

class Interpreter(StmtVisitor, ExprVisitor):
    """ Interprets a list of statements. """
    
    error_reporter: ErrorReporter
    """ The interpreter's error reporter. """
    
    globals: Environment
    """ The interpreter's global environment. """
    
    environment: Environment
    """ The interpreter's environment. """
    
    locals: dict[Expr, int]
    """ The interpreter's resolved local variables. """
    
    def __init__(self: Self, error_reporter: ErrorReporter) -> None:
        """ Initialize the interpreter. """
        
        super().__init__()
        self.error_reporter = error_reporter
        self.globals = Environment(error_reporter)
        self.environment = self.globals
        self.locals = {}
    
    
    def interpret(self: Self, statements: list[Stmt]) -> None:
        """ Interpret a list of statements. """
        
        # Install the standard library.
        ClockNativeFunction(self.globals)
        PrintNativeFunction(self.globals)
        
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
    
    
    def resolve(self: Self, expr: Expr, depth: int) -> None:
        """ Resolve an expression's variable to a depth. """
        
        self.locals[expr] = depth
    
    
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
    
    
    def visit_class_stmt(self: Self, stmt: ClassStmt) -> None:
        """ Visit and execute a class statement. """
        
        self.environment.define(stmt.name.lexeme, None)
        methods: dict[str, KroxFunction] = {}
        
        for method in stmt.methods:
            function: KroxFunction = KroxFunction(
                    self.error_reporter, self.execute_block,
                    method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function
        
        klass: KroxClass = KroxClass(
                self.error_reporter, stmt.name.lexeme, methods)
        self.environment.assign(stmt.name, klass)
    
    
    def visit_expression_stmt(self: Self, stmt: ExpressionStmt) -> None:
        """ Visit and execute an expression statement. """
        
        self.evaluate(stmt.expression)
    
    
    def visit_function_stmt(self: Self, stmt: FunctionStmt) -> None:
        """ Visit and execute a function statement. """
        
        function: KroxFunction = KroxFunction(
                self.error_reporter,
                self.execute_block, stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)
    
    
    def visit_if_stmt(self: Self, stmt: IfStmt) -> None:
        """ Visit and execute an if statement. """
        
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
    
    
    def visit_return_stmt(self: Self, stmt: ReturnStmt) -> None:
        """ Visit and execute a return statement. """
        
        value: Any = None
        
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        
        raise ReturnException(value)
    
    
    def visit_var_stmt(self: Self, stmt: VarStmt) -> None:
        """ Visit and execute a var statement. """
        
        value: Any = None
        
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value)
    
    
    def visit_while_stmt(self: Self, stmt: WhileStmt) -> None:
        """ Visit and execute a while statement. """
        
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
    
    
    def visit_assign_expr(self: Self, expr: AssignExpr) -> Any:
        """ Visit an assign expression and return a value. """
        
        value: Any = self.evaluate(expr.value)
        
        if expr in self.locals:
            self.environment.assign_at(self.locals[expr], expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        
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
    
    
    def visit_call_expr(self: Self, expr: CallExpr) -> Any:
        """ Visit a call expression and return a value. """
        
        callee: Any = self.evaluate(expr.callee)
        arguments: list[Any] = []
        
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        
        if not isinstance(callee, KroxCallable):
            raise self.error(
                    expr.paren, "Can only call functions and classes.")
        
        arity: int = callee.arity()
        
        if len(arguments) != arity:
            raise self.error(
                    expr.paren,
                    f"Expected {arity} arguments but got {len(arguments)}.")
        
        return callee.call(arguments)
    
    
    def visit_get_expr(self: Self, expr: GetExpr) -> Any:
        """ Visit a get expression and return a value. """
        
        object: Any = self.evaluate(expr.object)
        
        if not isinstance(object, KroxInstance):
            raise self.error(expr.name, "Only instances have properties.")
        
        return object.get(expr.name)
    
    
    def visit_grouping_expr(self: Self, expr: GroupingExpr) -> Any:
        """ Visit a grouping expression and return a value. """
        
        return self.evaluate(expr.expression)
    
    
    def visit_literal_expr(self: Self, expr: LiteralExpr) -> Any:
        """ Visit a literal expression and return a value. """
        
        return expr.value
    
    
    def visit_logical_expr(self: Self, expr: LogicalExpr) -> Any:
        """ Visit a logical expression and return a value. """
        
        left: Any = self.evaluate(expr.left)
        
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        
        return self.evaluate(expr.right)
    
    
    def visit_set_expr(self: Self, expr: SetExpr) -> Any:
        """ Visit a set expression and return a value. """
        
        object: Any = self.evaluate(expr.object)
        
        if not isinstance(object, KroxInstance):
            raise self.error(expr.name, "Only instances have fields.")
        
        value: Any = self.evaluate(expr.value)
        object.set(expr.name, value)
        return value
    
    
    def visit_this_expr(self: Self, expr: ThisExpr) -> Any:
        """ Visit a this expression and return a value. """
        
        return self.look_up_variable(expr.keyword, expr)
    
    
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
        
        return self.look_up_variable(expr.name, expr)
    
    
    def look_up_variable(self: Self, name: Token, expr: Expr) -> Any:
        """ Look up a variable's value from its name and expression. """
        
        if expr in self.locals:
            return self.environment.get_at(self.locals[expr], name.lexeme)
        else:
            return self.globals.get(name)
    
    
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
