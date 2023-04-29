from collections.abc import Callable
from krox_error_reporter import ErrorReporter
from krox_expr import AssignExpr, BinaryExpr, Expr, GroupingExpr, LiteralExpr
from krox_expr import UnaryExpr, VariableExpr
from krox_stmt import BlockStmt, ExpressionStmt, PrintStmt, Stmt, VarStmt
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
            if self.match(TokenType.VAR):
                return self.var_declaration()
            
            return self.statement()
        except SyntaxError:
            self.synchronize()
            return None
    
    
    def statement(self: Self) -> Stmt:
        """ Parse a statement. """
        
        if self.match(TokenType.PRINT):
            return self.print_statement()
        
        if self.match(TokenType.LEFT_BRACE):
            return BlockStmt(self.block())
        
        return self.expression_statement()
    
    
    def print_statement(self: Self) -> Stmt:
        """ Parse a print statement. """
        
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect `;` after value.")
        return PrintStmt(value)
    
    
    def var_declaration(self: Self) -> Stmt:
        """ Parse a var declaration. """
        
        name: Token = self.consume(
                TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Expr = (
                self.expression() if self.match(TokenType.EQUAL)
                else LiteralExpr(None))
        self.consume(
                TokenType.SEMICOLON, "Expect `;` after variable declaration.")
        return VarStmt(name, initializer)
    
    
    def expression_statement(self: Self) -> Stmt:
        """ Parse an expression statement. """
        
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect `;` after expression.")
        return ExpressionStmt(expr)
    
    
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
        
        expr: Expr = self.equality()
        
        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()
            
            if isinstance(expr, VariableExpr):
                name: Token = expr.name
                return AssignExpr(name, value)
            
            self.error(equals, "Invalid assignment target.")
        
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
        
        return self.primary()
    
    
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
        
        if self.match(TokenType.IDENTIFIER):
            return VariableExpr(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect `)` after expression.")
            return GroupingExpr(expr)
        
        raise self.error(self.peek(), "Expect expression.")
    
    
    def binary(
                self: Self,
                rule: Callable[[], Expr], *types: TokenType) -> Expr:
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
                    TokenType.PRINT, TokenType.RETURN):
                return
            
            self.advance()
