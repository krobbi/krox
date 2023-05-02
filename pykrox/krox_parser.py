from collections.abc import Callable
from krox_error_reporter import ErrorReporter
from krox_expr import AssignExpr, BinaryExpr, CallExpr, Expr, GetExpr
from krox_expr import GroupingExpr, LiteralExpr, LogicalExpr, SetExpr
from krox_expr import SuperExpr, ThisExpr, UnaryExpr, VariableExpr
from krox_stmt import BlockStmt, ClassStmt, ExpressionStmt, FunctionStmt
from krox_stmt import IfStmt, PrintStmt, ReturnStmt, Stmt, VarStmt, WhileStmt
from krox_token import Token
from krox_token_type import TokenType
from typing import Self

class Parser:
    """ Parses an abstract syntax tree from a list of tokens. """
    
    error_reporter: ErrorReporter
    """ The parser's error reporter. """
    
    tokens: list[Token]
    """ The tokens to parse. """
    
    current: int = 0
    """ The index of the current token. """
    
    def __init__(
            self: Self,
            error_reporter: ErrorReporter, tokens: list[Token]) -> None:
        """ Initialize the parser. """
        
        self.error_reporter = error_reporter
        self.tokens = tokens
    
    
    def parse(self: Self) -> list[Stmt]:
        """ Parse a list of statements. """
        
        statements: list[Stmt] = []
        
        while not self.is_at_end():
            declaration: Stmt | None = self.declaration()
            
            if declaration is not None:
                statements.append(declaration)
        
        return statements
    
    
    def expression(self: Self) -> Expr:
        """ Parse an expression. """
        
        return self.assignment()
    
    
    def declaration(self: Self) -> Stmt | None:
        """ Parse a declartion. """
        
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            
            if self.match(TokenType.FUN):
                return self.function("function")
            
            if self.match(TokenType.VAR):
                return self.var_declaration()
            
            return self.statement()
        except SyntaxError:
            self.synchronize()
            return None
    
    
    def class_declaration(self: Self) -> Stmt:
        """ Parse a class declaration. """
        
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        superclass: VariableExpr | None = None
        
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = VariableExpr(self.previous())
        
        self.consume(TokenType.LEFT_BRACE, "Expect `{` before class body.")
        methods: list[FunctionStmt] = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))
        
        self.consume(TokenType.RIGHT_BRACE, "Expect `}` after class body.")
        return ClassStmt(name, superclass, methods)
    
    
    def statement(self: Self) -> Stmt:
        """ Parse a statement. """
        
        if self.match(TokenType.FOR):
            return self.for_statement()
        
        if self.match(TokenType.IF):
            return self.if_statement()
        
        if self.match(TokenType.PRINT):
            return self.print_statement()
        
        if self.match(TokenType.RETURN):
            return self.return_statement()
        
        if self.match(TokenType.WHILE):
            return self.while_statement()
        
        if self.match(TokenType.LEFT_BRACE):
            return BlockStmt(self.block())
        
        return self.expression_statement()
    
    
    def for_statement(self: Self) -> Stmt:
        """ Parse a for statement. """
        
        self.consume(TokenType.LEFT_PAREN, "Expect `(` after `for`.")
        initializer: Stmt | None = None
        
        if self.match(TokenType.VAR):
            initializer = self.var_declaration()
        elif not self.match(TokenType.SEMICOLON):
            initializer = self.expression_statement()
        
        condition: Expr
        
        if self.match(TokenType.SEMICOLON):
            condition = LiteralExpr(True)
        else:
            condition = self.expression()
            self.consume(
                    TokenType.SEMICOLON, "Expect `;` after loop condition.")
        
        increment: Expr | None = None
        
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        
        self.consume(TokenType.RIGHT_PAREN, "Expect `)` after for clauses.")
        body: Stmt = self.statement()
        
        if increment is not None:
            body = BlockStmt([body, ExpressionStmt(increment)])
        
        body = WhileStmt(condition, body)
        
        if initializer is not None:
            body = BlockStmt([initializer, body])
        
        return body
    
    
    def if_statement(self: Self) -> Stmt:
        """ Parse an if statement. """
        
        self.consume(TokenType.LEFT_PAREN, "Expect `(` after `if`.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect `)` after if condition.")
        
        then_branch: Stmt = self.statement()
        else_branch: Stmt | None = None
        
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return IfStmt(condition, then_branch, else_branch)
    
    
    def print_statement(self: Self) -> Stmt:
        """ Parse a print statement. """
        
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect `;` after value.")
        return PrintStmt(value)
    
    
    def return_statement(self: Self) -> Stmt:
        """ Parse a return statement. """
        
        keyword: Token = self.previous()
        value: Expr | None = None
        
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect `;` after return value.")
        return ReturnStmt(keyword, value)
    
    
    def var_declaration(self: Self) -> Stmt:
        """ Parse a var declaration. """
        
        name: Token = self.consume(
                TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Expr | None = None
        
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(
                TokenType.SEMICOLON, "Expect `;` after variable declaration.")
        return VarStmt(name, initializer)
    
    
    def while_statement(self: Self) -> Stmt:
        """ Parse a while statement. """
        
        self.consume(TokenType.LEFT_PAREN, "Expect `(` after while.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect `)` after condition.")
        body: Stmt = self.statement()
        return WhileStmt(condition, body)
    
    
    def expression_statement(self: Self) -> Stmt:
        """ Parse an expression statement. """
        
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect `;` after expression.")
        return ExpressionStmt(expr)
    
    
    def function(self: Self, kind: str) -> FunctionStmt:
        """ Parse a function statement. """
        
        name: Token = self.consume(
                TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect `(` after {kind} name.")
        parameters: list[Token] = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(
                    TokenType.IDENTIFIER, "Expect parameter name."))
            
            while self.match(TokenType.COMMA):
                parameters.append(self.consume(
                        TokenType.IDENTIFIER, "Expect parameter name."))
        
        self.consume(TokenType.RIGHT_PAREN, "Expect `)` after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect `{{` before {kind} body.")
        body: list[Stmt] = self.block()
        return FunctionStmt(name, parameters, body)
    
    
    def block(self: Self) -> list[Stmt]:
        """ Parse a list of statements from a block statement. """
        
        statements: list[Stmt] = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            declaration: Stmt | None = self.declaration()
            
            if declaration is not None:
                statements.append(declaration)
        
        self.consume(TokenType.RIGHT_BRACE, "Expect `}` after block.")
        return statements
    
    
    def assignment(self: Self) -> Expr:
        """ Parse an assignment expression. """
        
        expr: Expr = self.or_expression()
        
        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()
            
            if isinstance(expr, VariableExpr):
                name: Token = expr.name
                return AssignExpr(name, value)
            elif isinstance(expr, GetExpr):
                return SetExpr(expr.object, expr.name, value)
            
            self.error(equals, "Invalid assignment target.")
        
        return expr
    
    
    def or_expression(self: Self) -> Expr:
        """ Parse an or expression. """
        
        expr: Expr = self.and_expression()
        
        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.and_expression()
            expr = LogicalExpr(expr, operator, right)
        
        return expr
    
    
    def and_expression(self: Self) -> Expr:
        """ Parse an and expression. """
        
        expr: Expr = self.equality()
        
        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr = self.equality()
            expr = LogicalExpr(expr, operator, right)
        
        return expr
    
    
    def equality(self: Self) -> Expr:
        """ Parse an equality expression. """
        
        return self.binary(
                self.comparison, TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL)
    
    
    def comparison(self: Self) -> Expr:
        """ Parse a comparison expression. """
        
        return self.binary(
                self.term, TokenType.GREATER, TokenType.GREATER_EQUAL,
                TokenType.LESS, TokenType.LESS_EQUAL)
    
    
    def term(self: Self) -> Expr:
        """ Parse a term expression. """
        
        return self.binary(self.factor, TokenType.MINUS, TokenType.PLUS)
    
    
    def factor(self: Self) -> Expr:
        """ Parse a factor expresison. """
        
        return self.binary(self.unary, TokenType.SLASH, TokenType.STAR)
    
    
    def unary(self: Self) -> Expr:
        """ Parse a unary expression. """
        
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return UnaryExpr(operator, right)
        
        return self.call()
    
    
    def call(self: Self) -> Expr:
        """ Parse a call expression. """
        
        expr: Expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name: Token = self.consume(
                        TokenType.IDENTIFIER,
                        "Expect property name after `.`.")
                expr = GetExpr(expr, name)
            else:
                break
        
        return expr
    
    
    def finish_call(self: Self, callee: Expr) -> Expr:
        """ Finish a call expression. """
        
        arguments: list[Expr] = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            
            while self.match(TokenType.COMMA):
                arguments.append(self.expression())
        
        paren: Token = self.consume(
                TokenType.RIGHT_PAREN, "Expect `)` after arguments.")
        
        if len(arguments) >= 255:
            self.error(paren, "Can't have more than 255 arguments.")
        
        return CallExpr(callee, paren, arguments)
    
    
    def primary(self: Self) -> Expr:
        """ Parse a primary expression. """
        
        if self.match(TokenType.FALSE):
            return LiteralExpr(False)
        
        if self.match(TokenType.TRUE):
            return LiteralExpr(True)
        
        if self.match(TokenType.NIL):
            return LiteralExpr(None)
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self.previous().literal)
        
        if self.match(TokenType.SUPER):
            keyword: Token = self.previous()
            self.consume(TokenType.DOT, "Expect `.` after `super`.")
            method: Token = self.consume(
                    TokenType.IDENTIFIER, "Expect superclass method name.")
            return SuperExpr(keyword, method)
        
        if self.match(TokenType.THIS):
            return ThisExpr(self.previous())
        
        if self.match(TokenType.IDENTIFIER):
            return VariableExpr(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect `)` after expression.")
            return GroupingExpr(expr)
        
        raise self.error(self.peek(), "Expect expression.")
    
    
    def binary(
            self: Self, rule: Callable[[], Expr], *types: TokenType) -> Expr:
        """
        Parse a left-associative binary expression from its
        sub-expression rule and operator types.
        """
        
        expr: Expr = rule()
        
        while self.match(*types):
            operator: Token = self.previous()
            right: Expr = rule()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    
    def match(self: Self, *types: TokenType) -> bool:
        """
        Consume the current token if it matches a set of types and
        return whether the token was consumed.
        """
        
        for type in types:
            if self.check(type):
                self.advance()
                return True
        
        return False
    
    
    def consume(self: Self, type: TokenType, message: str) -> Token:
        """
        Consume and return the current token if it matches a type.
        Otherwise, log an error and enter panic mode.
        """
        
        if self.check(type):
            return self.advance()
        
        raise self.error(self.peek(), message)
    
    
    def check(self: Self, type: TokenType) -> bool:
        """ Return whether the current token matches a type. """
        
        if self.is_at_end():
            return False
        
        return self.peek().type == type
    
    
    def advance(self: Self) -> Token:
        """ Consume and return the current token. """
        
        if not self.is_at_end():
            self.current += 1
        
        return self.previous()
    
    
    def is_at_end(self: Self) -> bool:
        """ Return whether all of the tokens have been consumed. """
        
        return self.peek().type == TokenType.EOF
    
    
    def peek(self: Self) -> Token:
        """ Peek the current token. """
        
        return self.tokens[self.current]
    
    
    def previous(self: Self) -> Token:
        """ Peek the previous token. """
        
        return self.tokens[self.current - 1]
    
    
    def error(self: Self, token: Token, message: str) -> SyntaxError:
        """
        Report an error from a token and a message and return a syntax
        error.
        """
        
        self.error_reporter.error(token, message)
        return SyntaxError()
    
    
    def synchronize(self: Self) -> None:
        """ Advance the parser to a stable state after panicking. """
        
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in (
                    TokenType.CLASS, TokenType.FUN, TokenType.VAR,
                    TokenType.FOR, TokenType.IF, TokenType.WHILE,
                    TokenType.RETURN):
                return
            
            self.advance()
