#!/usr/bin/env python

import sys

from krox_error_reporter import ErrorReporter
from krox_scanner import Scanner
from krox_token import Token
from typing import Self

class Krox:
    """ Java-style main class to match the JLox implementation. """
    
    error_reporter: ErrorReporter
    """ The error reporter to pass through the interpreter. """
    
    def __init__(self: Self) -> None:
        """ Initialize Krox. """
        
        self.error_reporter = ErrorReporter()
    
    
    def main(self: Self, args: list[str]) -> None:
        """ Run Krox from arguments. """
        
        if len(args) > 1:
            print("Usage: krox.py [script]")
            sys.exit(64)
        elif len(args) == 1:
            self.run_file(args[0])
        else:
            self.run_prompt()
    
    
    def run_file(self: Self, path: str) -> None:
        """ Run Krox from a file path. """
        
        with open(path) as file:
            self.run(file.read())
            
            if self.error_reporter.had_error():
                sys.exit(65)
    
    
    def run_prompt(self: Self) -> None:
        """ Run Krox from a prompt. """
        
        while True:
            try:
                line: str = input("> ")
                self.run(line)
                self.error_reporter.clear()
            except EOFError:
                break
    
    
    def run(self: Self, source: str) -> None:
        """ Run Krox from source code. """
        
        if source == "$test":
            self.test()
            return
        
        scanner: Scanner = Scanner(self.error_reporter, source)
        tokens: list[Token] = scanner.scan_tokens()
        
        for token in tokens:
            print(token)
    
    
    def test(self: Self) -> None:
        """ Test Krox. """
        
        from krox_ast_printer import ASTPrinter
        from krox_expr import BinaryExpr, Expr, GroupingExpr, LiteralExpr
        from krox_expr import UnaryExpr
        from krox_token import Token
        from krox_token_type import TokenType
        
        # Equivalent to `-123 * (45.67)`.
        expression: Expr = BinaryExpr(
                UnaryExpr(
                        Token(TokenType.MINUS, "-", None, 1),
                        LiteralExpr(123)),
                Token(TokenType.STAR, "*", None, 1),
                GroupingExpr(
                        LiteralExpr(45.67)))
        
        result: str = ASTPrinter().print(expression)
        print(result)
        
        assert result == "(* (- 123) (group 45.67))", "AST printer failed!"


if __name__ == "__main__":
    krox: Krox = Krox()
    krox.main(sys.argv[1:])
