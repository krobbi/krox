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
        
        scanner: Scanner = Scanner(self.error_reporter, source)
        tokens: list[Token] = scanner.scan_tokens()
        
        for token in tokens:
            print(token)


if __name__ == "__main__":
    krox: Krox = Krox()
    krox.main(sys.argv[1:])
