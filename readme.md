# Krox
_Following Crafting Interpreters._  
__Copyright &copy; 2023 Chris Roberts__ (Krobbizoid).

# Contents
1. [About](#about)
2. [Design](#design)
3. [About Lox](#about-lox)
4. [Lox Extensions](#lox-extensions)
   * [`x_arg(index)`](#x_argindex)
   * [`x_args()`](#x_args)
   * [`x_chr(code)`](#x_chrcode)
   * [`x_close(handle)`](#x_closehandle)
   * [`x_get(handle)`](#x_gethandle)
   * [`x_length(string)`](#x_lengthstring)
   * [`x_ord(character)`](#x_ordcharacter)
   * [`x_put(byte, handle)`](#x_putbyte-handle)
   * [`x_read(path)`](#x_readpath)
   * [`x_stderr()`](#x_stderr)
   * [`x_stdin()`](#x_stdin)
   * [`x_stdout()`](#x_stdout)
   * [`x_substring(string, start, length)`](#x_substringstring-start-length)
   * [`x_trunc(number)`](#x_truncnumber)
   * [`x_write(path)`](#x_writepath)
5. [License](#license)

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
// From `module.krox`, import `foo` and `bar` renamed to `baz`.
> "module.krox" {
   foo,
   bar > baz,
}

// Renaming imports helps prevent collisions.
fn bar(){}

// Declarations can be exported using `<`.
< fn square(x){
   return x * x;
}

// A `main` function is reserved to allow the program to execute.
fn main(){}
```

To handle this, each module must keep track of its own set of available
identifiers, and each declaration must have a unique ID to allow declarations
of the same identifier.

A simplified example of the data needed for the above module is shown below:
```json
{
   "globals": {
      "foo": "module.krox:foo",
      "baz": "module.krox:bar",
      "bar": "main.krox:bar",
      "square": "main.krox:square",
      "main": "main.krox:main"
   },
   "exports": [
      "square"
   ]
}
```

An incomplete grammar for Krox is shown below:
```ebnf
module = { top }, EOF ;
top = imports | export | declaration ;
imports = ">", STRING, "{", [ import ], "}" ;
import = IDENTIFIER, [ ">", IDENTIFIER ], [ ",", [ import ] ] ;
export = "<", declaration ;
declaration = function ;
```

# About Lox
Lox is a language described in the book
[Crafting Interpreters](https://craftinginterpreters.com) by
[Robert Nystrom](https://github.com/munificent). The language is implemented
twice over the course of the book. First with a tree-walk interpreter written
in Java, and then with a bytecode interpreter written in C.

I followed along with the book to get a better idea of the best practices and
design choices involved in designing a language. Lox also has object-oriented
capabilities, which I had never previously attempted to implement.

My initial implementation of Lox was written in Python instead of Java for
convenience.

# Lox Extensions
In addition to the standard `clock()` function, my implementation of Lox
includes some extension functions to improve its I/O capabilities. The
non-standard extensions are marked with an `x_` prefix to indicate that they
have a special implementation and to reduce namespace pollution.

## `x_arg(index)`
Return the command line argument string at index `index`, following the same
range as `x_args()`. The first argument is at index `0`. Using an out of range
index returns `nil`.

## `x_args()`
Return the number of command line arguments, starting at and including the Lox
script file's name. This function should always return `0` in REPL mode, and
always return at least `1` when outside of REPL mode.

## `x_chr(code)`
Return a single character string with the number code point `code`. Returns
`nil` if `code` is not a number from `0` to `255`.

## `x_close(handle)`
Flush and close the stream at the file handle number `handle`. Returns `true`
if a file stream was closed successfully. Otherwise, returns `false`.
Attempting to close a standard stream will do nothing and always return
`false`.

## `x_get(handle)`
Get and return the next byte from the stream at the file handle number
`handle`. Returns `nil` if an error or the end of file was encountered.
Otherwise, returns a number from `0` to `255`.

## `x_length(string)`
Return the number length of the string `string` in characters. Returns an
undefined number value if `string` is not a string.

## `x_ord(character)`
Return the number code point of the single character string `character`.
Returns `nil` if `character` is not a single character or has a code point
outside of the range of `0` to `255`.

## `x_put(byte, handle)`
Put a byte number `byte` from `0` to `255` to the stream at the file handle
number `handle`. Returns `nil` if the byte number could not be put to a stream
for any reason. Otherwise, returns the byte number that was written.

## `x_read(path)`
Open the file at the path string `path` for reading and return a file handle
number. Returns `nil` if the file could not be opened for any reason. Any
returned file handle number must later be closed with `x_close(handle)`.

## `x_stderr()`
Return a file handle number representing the standard error stream. Always
returns `2`.

## `x_stdin()`
Return a file handle number representing the standard input stream. Always
returns `0`.

## `x_stdout()`
Return a file handle number representing the standard output stream. Always
returns `1`.

## `x_substring(string, start, length)`
Return a new substring of `string` starting at index `start` with length
`length`. Returns `nil` if `length` is negative or if the substring would be
out of bounds of `string`.

## `x_trunc(number)`
Return the number `number` with any fractional part truncated, rounding towards
`0`. Returns an undefined number value if `number` is not a number.

## `x_write(path)`
Open the file at the path string `path` for writing and return a file hande
number. Returns `nil` if the file could not be opened for any reason. Any
returned file handle number must later be closed with `x_close(handle)`.

# License
Krox is released under the MIT License:  
https://krobbi.github.io/license/2023/mit.txt

See [license.txt](./license.txt) for a full copy of the license text.
