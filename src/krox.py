#!/usr/bin/env python

import sys

from krox_ast_printer import ASTPrinter
from krox_error_reporter import ErrorReporter
from krox_interpreter import Interpreter
from krox_parser import Parser
from krox_scanner import Scanner
from krox_stmt import Stmt
from krox_token import Token
from typing import Self

class Krox:
    """ Java-style main class to match the JLox implementation. """
    
    error_reporter: ErrorReporter
    """ The error reporter to pass through the interpreter. """
    
    interpreter: Interpreter
    """ The Krox interpreter. """
    
    def __init__(self: Self) -> None:
        """ Initialize Krox. """
        
        self.error_reporter = ErrorReporter()
        self.interpreter = Interpreter(self.error_reporter)
    
    
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
        
        self.interpreter.interpret(statements)


if __name__ == "__main__":
    krox: Krox = Krox()
    krox.main(sys.argv[1:])
