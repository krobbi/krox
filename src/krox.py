#!/usr/bin/env python

import sys

from typing import Self

class Krox:
    """ Java-style main class to match the JLox implementation. """
    
    def main(self: Self, args: list[str]) -> None:
        """ Run Krox from arguments. """
        
        print("Hello, Krox!")


if __name__ == "__main__":
    krox: Krox = Krox()
    krox.main(sys.argv[1:])
