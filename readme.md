# Krox
_Following Crafting Interpreters._  
__Copyright &copy; 2023 Chris Roberts__ (Krobbizoid).

# Contents
1. [About](#about)
2. [Differences from Lox](#differences-from-lox)
3. [Standard Library](#standard-library)
   * [`clock`](#clock)
   * [`input`](#input)
   * [`print`](#print)
4. [License](#license)

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
and design choices involved in designing a language. Lox also appears to be
much more practical than Funcy, and has object oriented capabilities, which I
have never attempted to implement.

The initial implementation of Krox has been written in Python as I find it much
more convenient than Java. I am experimenting with potential features in the
Python implementation before creating the C implementation in part 3 of the
book.

Finally, I intend for Krox to diverge away from Lox and gain features to become
more practical.

# Differences from Lox
* Krox is named 'Krox' instead of 'Lox'.
* The `print` statement has been replaced with a native function. Because of
this, parentheses are required for printing. The `print` function always
returns `nil`.
* The standard library has been expanded to include more useful I/O features.

# Standard Library
Krox includes some standard functions for input, output, and timing.

The parameter and return types for these functions are notated below with
`[any]`, `[nil]`, `[bool]`, `[number]`, and `[string]`. Please note that Krox
is dynamically typed and does not support a type notation system. Any arguments
that do not match the parameter type will silently be cast to it.

## `clock`
Return the number of seconds since the program started.

__Signature:__  
`clock() -> [number]`

__Parameters:__  
* _None._

__Return value:__  
`[number]` - The duration since the program started in seconds. Includes a
fractional part.

## `input`
Read input from the user.

__Signature:__  
`input(prompt: [string]) -> [string]`

__Parameters:__  
* `prompt: [string]` - The prompt message to display to the user. The prompt is
displayed as text and the user must input a line of text immediately following
it. The program halts until the user presses return to input the text. After
the text is input, a trailing line break is displayed.

__Return value:__  
`[string]` - The text inputted by the user. If the user pressed return without
inputting any text then this will be an empty string.

## `print`
Display a value to the user.

__Signature:__  
`print(value: [any]) -> [nil]`

__Parameters:__  
* `value: [any]` - The value to display to the user. All types of values are
displayed as text with a trailing line break.

__Return value:__  
`[nil]` - No value. The function is not intended to be called outside of
standalone expressions.

# License
Krox is released under the MIT License:  
https://krobbi.github.io/license/2023/mit.txt

See [license.txt](./license.txt) for a full copy of the license text.
