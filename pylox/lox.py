#!/usr/bin/env python

import sys

from lox_ast_printer import ASTPrinter
from lox_error_reporter import ErrorReporter
from lox_interpreter import Interpreter
from lox_parser import Parser
from lox_resolver import Resolver
from lox_scanner import Scanner
from lox_stmt import Stmt
from lox_token import Token
from typing import Self

class Lox:
    """ Java-style main class to match the jlox implementation. """
    
    error_reporter: ErrorReporter
    """ The error reporter to pass through the interpreter. """
    
    interpreter: Interpreter
    """ The Lox interpreter. """
    
    def __init__(self: Self) -> None:
        """ Initialize Lox. """
        
        self.error_reporter = ErrorReporter()
        self.interpreter = Interpreter(self.error_reporter)
    
    
    def main(self: Self, args: list[str]) -> None:
        """ Run Lox from arguments. """
        
        if args:
            self.run_file(args[0])
        else:
            self.run_prompt()
    
    
    def run_file(self: Self, path: str) -> None:
        """ Run Lox from a file path. """
        
        with open(path) as file:
            self.run(file.read())
            
            if self.error_reporter.had_error():
                sys.exit(65)
    
    
    def run_prompt(self: Self) -> None:
        """ Run Lox from a prompt. """
        
        while True:
            try:
                line: str = input("> ")
                self.run(line)
                self.error_reporter.clear()
            except EOFError:
                break
    
    
    def run(self: Self, source: str) -> None:
        """ Run Lox from source code. """
        
        scanner: Scanner = Scanner(self.error_reporter, source)
        tokens: list[Token] = scanner.scan_tokens()
        parser: Parser = Parser(self.error_reporter, tokens)
        statements: list[Stmt] = parser.parse()
        
        if self.error_reporter.had_error():
            return
        
        if source.endswith("//ast"):
            ast_printer: ASTPrinter = ASTPrinter()
            
            for statement in statements:
                print(ast_printer.print(statement))
            
            return
        
        resolver: Resolver = Resolver(self.error_reporter, self.interpreter)
        resolver.resolve(statements)
        
        if self.error_reporter.had_error():
            return
        
        self.interpreter.interpret(statements)


if __name__ == "__main__":
    lox: Lox = Lox()
    lox.main(sys.argv[1:])
