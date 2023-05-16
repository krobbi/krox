# Krox
_Following Crafting Interpreters._  
__Copyright &copy; 2023 Chris Roberts__ (Krobbizoid).

# Contents
1. [About](#about)
2. [About Lox](#about-lox)
3. [Lox Extensions](#lox-extensions)
   * [`arg(index)`](#argindex)
   * [`args()`](#args)
   * [`close(handle)`](#closehandle)
   * [`get(handle)`](#gethandle)
   * [`put(byte, handle)`](#putbyte-handle)
   * [`read(path)`](#readpath)
   * [`stderr()`](#stderr)
   * [`stdin()`](#stdin)
   * [`stdout()`](#stdout)
   * [`write(path)`](#writepath)
3. [License](#license)

# About
Krox is a language that is yet to be created, loosely based on some insight
from the Lox language.

I have attempted to write languages before Krox, most notably
[Funcy](https://github.com/krobbi/funcy), which was implemented in Python.
Funcy was used as a testing ground for implementing functions in NightScript, a
scripting language that was used for cutscenes in my game,
[Coldest Night](https://github.com/krobbi/coldest-night). NightScript has since
been removed from the game and I am now leveraging the game engine's
functionality, as I should have in the first place.

Originally, Krox was planned to be an extension of Lox, but its scope would
make it difficult to fit into a Lox interpreter.

Despite this, I still intend on implementing Krox in Lox, which will be a
serious challenge.

# About Lox
Lox is a language described in the book
[Crafting Interpreters](https://craftinginterpreters.com) by
[Robert Nystrom](https://github.com/munificent). The language is implemented
twice over the course of the book. First with a tree-walk interpreter written
in Java, and then with a bytecode interpreter written in C.

I followed along with the book to get a better idea of the best practices and
design choices involved in designing a language. Lox also has object-oriented
capabilities, which I had never previously attempted to implement.

My initial implementation of Lox was written in Python instead of Java.

_This repository contains:_  
* `Makefile` - Makefile for bootstrapping Krox. Designed for Windows. Currently
a hello world. Use at your own risk.
* `clox/` - A completed Lox interpreter witten in C.
* `loxkrox/` - An unimplemented Krox interpreter written in Lox. Currently a
hello world.
* `pylox/` - A completed Lox interpreter written in Python. Too slow for most
practical uses.
* `sample/` - Sample Lox code.

# Lox Extensions
In addition to the standard `clock()` function, my implementation of Lox
includes some 'extension' functions to improve its I/O capabilities.

## `arg(index)`
Return the command line argument string at index `index`, following the same
range as `args()`. The first argument is at index `0`. Using an out of range
index returns `nil`.

## `args()`
Return the number of command line arguments, starting at and including the Lox
script file's name. This function should always return `0` in REPL mode, and
always return at least `1` when outside of REPL mode.

## `close(handle)`
Flush and close the stream at the file handle number `handle`. Returns `true`
if a file stream was closed successfully. Otherwise, returns `false`.
Attempting to close a standard stream will do nothing and always return
`false`.

## `get(handle)`
Get and return the next byte from the stream at the file handle number
`handle`. Returns `nil` if an error or the end of file was encountered.
Otherwise, returns a number from `0` to `255`.

## `put(byte, handle)`
Put a byte number `byte` from `0` to `255` to the stream at the file handle
number `handle`. Returns `nil` if the byte number could not be put to a stream
for any reason. Otherwise, returns the byte number that was written.

## `read(path)`
Open the file at the path string `path` for reading and return a file handle
number. Returns `nil` if the file could not be opened for any reason. Any
returned file handle number must later be closed with `close(handle)`.

## `stderr()`
Return a file handle number representing the standard error stream. Always
returns `2`.

## `stdin()`
Return a file handle number representing the standard input stream. Always
returns `0`.

## `stdout()`
Return a file handle number representing the standard output stream. Always
returns `1`.

## `write(path)`
Open the file at the path string `path` for writing and return a file hande
number. Returns `nil` if the file could not be opened for any reason. Any
returned file handle number must later be closed with `close(handle)`.

# License
Krox is released under the MIT License:  
https://krobbi.github.io/license/2023/mit.txt

See [license.txt](./license.txt) for a full copy of the license text.
