# Krox
_Following Crafting Interpreters._  
__Copyright &copy; 2023 Chris Roberts__ (Krobbizoid).

# Contents
1. [About](#about)
2. [License](#license)

# About
Krox is a programming language that is gradually being created as I follow
along with the book [Crafting Interpreters](https://craftinginterpreters.com)
by [Robert Nystrom](https://github.com/munificent).

The book describes a language named Lox that is implemented over the course of
the book. First with a tree-walk interpreter written in Java, and then with a
bytecode interpreter written in C.

I have attempted to write languages before, most notably
[Funcy](https://github.com/krobbi/funcy), which was implemented in Python.
Funcy was used as a testing ground for implementing functions in NightScript, a
scripting language that was used for cutscenes in my game,
[Coldest Night](https://github.com/krobbi/coldest-night). NightScript has since
been removed from the game and I am now leveraging the game engine's
functionality, as I should have in the first place.

I am following along with the book to get a better idea of the best practices
and design choices involved in designing a language. Lox also is much more
practical than Funcy, and has object oriented capabilities, which I had never
previously attempted to implement.

The initial implementation of Krox was written in Python as I found it much
more convenient than Java. I am now implementing the C version from part 3 of
the book, which introduces replaces the parsing stage with single-pass
compilation.

Finally, I intend for Krox to diverge away from Lox and gain features to become
more practical.

_This repository contains:_  
* `Makefile` - Makefile for CKrox. Designed for Windows. Use at your own risk.
* `ckrox/` - An unfinished interpreter witten in C.
* `pykrox/` - A completed interpreter written in Python following the standard
implementation of Lox.
* `sample/` - Sample Krox code.

# License
Krox is released under the MIT License:  
https://krobbi.github.io/license/2023/mit.txt

See [license.txt](./license.txt) for a full copy of the license text.
