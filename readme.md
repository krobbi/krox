# Krox
_Ongoing language project._  
__Copyright &copy; 2023 Chris Roberts__ (Krobbizoid).

# Contents
1. [About](#about)
2. [Design](#design)
3. [About Lox](#about-lox)
4. [Lox Implementation Details](#lox-implementation-details)
5. [Lox Intrinsics](#lox-intrinsics)
   * [`_argc()`](#_argc)
   * [`_argv(index)`](#_argvindex)
   * [`_chr(code)`](#_chrcode)
   * [`_close(handle)`](#_closehandle)
   * [`_get(handle)`](#_gethandle)
   * [`_length(string)`](#_lengthstring)
   * [`_ord(character)`](#_ordcharacter)
   * [`_put(byte, handle)`](#_putbyte-handle)
   * [`_read(path)`](#_readpath)
   * [`_stderr()`](#_stderr)
   * [`_stdin()`](#_stdin)
   * [`_stdout()`](#_stdout)
   * [`_substring(string, start, length)`](#_substringstring-start-length)
   * [`_trunc(number)`](#_truncnumber)
   * [`_write(path)`](#_writepath)
6. [License](#license)

# About
Krox is an unfinished language whose initial implementation is being written in
Lox. Originally, Krox was planned to be an extension of Lox, but its scope
would make it difficult to fit into a Lox interpreter. See
[About Lox](#about-lox) for more information about the Lox language.

I have attempted to write languages before Krox, most notably
[Funcy](https://github.com/krobbi/funcy), which was implemented in Python.
Funcy was used as a testing ground for implementing functions in NightScript, a
scripting language that was used for cutscenes in my game,
[Coldest Night](https://github.com/krobbi/coldest-night). NightScript has since
been removed from the game and I am now leveraging the game engine's
functionality, as I should have in the first place.

_This repository contains:_  
* `Makefile` - Makefile for bootstrapping Krox. Designed for Windows. Currently
unfinished. Use at your own risk.
* `clox/` - A Lox interpreter witten in C.
* `etc/lox/` - Sample Lox code.
* `etc/pylox/` - A Lox interpreter written in Python. Too slow for most
practical purposes and not used by the rest of the repository.
* `loxkrox/` - An unfinished Krox compiler written in Lox.

# Design
A major planned feature of Krox is an import system capable of importing and
renaming individual identifiers from modules, and allowing top level
identifiers to be used regardless of the order they are declared in. To make
this easier to implement, top level code must only consist of imports and
declarations.

An example of potential Krox code is shown below:
```
import "module.krox" {
   foo,
   bar as baz, // Imports can be renamed.
}

// Renaming imports helps prevent collisions.
fn bar(){}

// Imports and exports can appear at any point at the top level.
export {
   square,
   baz as qux, // Exports can be renamed and use imported identifiers.
}

fn square(x){
   return x * x;
}

// A `main` function is reserved to allow the program to execute.
fn main(){}
```

See [grammar.ebnf](./grammar.ebnf) for an incomplete Krox grammar.

# About Lox
Lox is a language described in the book
[Crafting Interpreters](https://craftinginterpreters.com) by
[Bob Nystrom](https://github.com/munificent). The language is implemented twice
over the course of the book. First with a tree-walk interpreter written in
Java, and then with a bytecode interpreter written in C.

Lox supports global and local dynamic variables, functions with closures, and
classes and instances with single inheritance. Functions and classes are first
class, and can be passed around as variables.

The Krox project began with following along with the book to get a better idea
of the best practices and design choices involved in designing a language, and
to better understand how object oriented languages may be implemented.

# Lox Implementation Details
My initial implementation of Lox was written in Python instead of Java for
convenience.

My C implementation of Lox merges constants with equal values to the same
constant ID. This increases compilation time, but allows programs to grow
larger without running out of constant IDs.

The size of constant IDs in the C implementation has been increased from 8 bits
to 16 bits. This adds a lot of redundant data to the internal bytecode in most
cases, but was simpler to implement than separate long constant opcodes.
Additional constant IDs have become necessary to implement the Krox compiler.

# Lox Intrinsics
In addition to the standard `clock()` function, my implementation of Lox
includes some intrinsic functions to improve its capabilities in ways that are
not normally possible to implement in Lox. These non-standard intrinsics are
marked with an `_` prefix to indicate that they have a special implementation
and reduce namespace pollution.

## `_argc()`
Return the number of command line arguments, starting at and including the Lox
script file's name. Always returns `0` in REPL mode and at least `1` outside of
REPL mode.

## `_argv(index)`
Return the command line argument string at index `index`. Returns `nil` if
`index` is less than `0` or greater than or equal to `_argc()`.

## `_chr(code)`
Return a single character string with the number code point `code`. Returns
`nil` if `code` is not a number from `0` to `255`.

## `_close(handle)`
Flush and close the stream at the file handle number `handle`. Returns `true`
if a file stream was closed successfully. Otherwise, returns `false`.
Attempting to close a standard stream will do nothing and always return
`false`.

## `_get(handle)`
Get and return the next byte from the stream at the file handle number
`handle`. Returns `nil` if an error or the end of file was encountered.
Otherwise, returns a number from `0` to `255`.

## `_length(string)`
Return the number length of the string `string` in characters. Returns an
undefined number value if `string` is not a string.

## `_ord(character)`
Return the number code point of the single character string `character`.
Returns `nil` if `character` is not a single character or has a code point
outside of the range of `0` to `255`.

## `_put(byte, handle)`
Put a byte number `byte` from `0` to `255` to the stream at the file handle
number `handle`. Returns `nil` if the byte number could not be put to a stream
for any reason. Otherwise, returns the byte number that was written.

## `_read(path)`
Open the file at the path string `path` for reading and return a file handle
number. Returns `nil` if the file could not be opened for any reason. Any
returned file handle number must later be closed with `_close(handle)`.

## `_stderr()`
Return a file handle number representing the standard error stream. Always
returns `2`.

## `_stdin()`
Return a file handle number representing the standard input stream. Always
returns `0`.

## `_stdout()`
Return a file handle number representing the standard output stream. Always
returns `1`.

## `_substring(string, start, length)`
Return a new substring of `string` starting at index `start` with length
`length`. Returns `nil` if `length` is negative or if the substring would be
out of bounds of `string`.

## `_trunc(number)`
Return the number `number` with any fractional part truncated, rounding towards
`0`. Returns an undefined number value if `number` is not a number.

## `_write(path)`
Open the file at the path string `path` for writing and return a file hande
number. Returns `nil` if the file could not be opened for any reason. Any
returned file handle number must later be closed with `_close(handle)`.

# License
Krox is released under the MIT License:  
https://krobbi.github.io/license/2023/mit.txt

See [license.txt](./license.txt) for a full copy of the license text.
