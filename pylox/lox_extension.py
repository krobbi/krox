import sys

from collections.abc import Callable
from typing import Any, BinaryIO

STREAMS: list[BinaryIO | None] = [
    sys.stdin.buffer,
    sys.stdout.buffer,
    sys.stderr.buffer,
    None,
    None,
    None,
    None,
    None,
]
""" Streams available to Lox. """

def arg_extension(arguments: list[Any]) -> str | None:
    """ The arg extension. """
    
    index: int = int(arguments[0]) + 1
    
    if index < 1 or index >= len(sys.argv):
        return None
    
    return sys.argv[index]


def args_extension(arguments: list[Any]) -> float:
    """ The args extension. """
    
    return float(max(len(sys.argv) - 1, 0))


def put_extension(arguments: list[Any]) -> float | None:
    """ The put extension. """
    
    byte: int = int(arguments[0])
    
    if byte < 0 or byte > 255:
        return None # Invalid byte.
    
    handle: int = int(arguments[1])
    
    if handle < 0 or handle >= len(STREAMS):
        return None # Invalid file handle.
    
    stream: BinaryIO | None = STREAMS[handle]
    
    if stream is None:
        return None # Unopened stream.
    
    try:
        stream.write(bytes((byte,)))
    except (OSError, ValueError):
        return None # Failed to put byte.
    
    return float(byte)


def define_constant(
        define_native: Callable[[str, int, Callable[[list[Any]], Any]], None],
        name: str, value: Any) -> None:
    """ Define a constant function. """
    
    def constant(arguments: list[Any]) -> Any:
        """ Return a constant value. """
        
        return value
    
    define_native(name, 0, constant)


def install_extensions(
        define_native: Callable[
                [str, int, Callable[[list[Any]], Any]], None]) -> None:
    """ Install the extensions. """
    
    define_native("arg", 1, arg_extension)
    define_native("args", 0, args_extension)
    define_native("put", 2, put_extension)
    define_constant(define_native, "stderr", 2)
    define_constant(define_native, "stdin", 0)
    define_constant(define_native, "stdout", 1)
