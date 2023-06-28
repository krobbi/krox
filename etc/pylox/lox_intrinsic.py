import math
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

FILE_HANDLE_MIN: int = 3
""" The minimum file handle available to lox. """

def argc_intrinsic(arguments: list[Any]) -> float:
    """ The argc intrinsic. """
    
    return float(max(len(sys.argv) - 1, 0))


def argv_intrinsic(arguments: list[Any]) -> str | None:
    """ The argv intrinsic. """
    
    index: int = int(arguments[0]) + 1
    
    if index < 1 or index >= len(sys.argv):
        return None # Argument out of range.
    
    return sys.argv[index]


def chr_intrinsic(arguments: list[Any]) -> str | None:
    """ The chr intrinsic. """
    
    code: int = int(arguments[0])
    
    if code < 0 or code > 255:
        return None # Not an ASCII character.
    
    return chr(code)


def close_intrinsic(arguments: list[Any]) -> bool:
    """ The close intrinsic. """
    
    handle: int = int(arguments[0])
    
    if handle < FILE_HANDLE_MIN or handle >= len(STREAMS):
        return False # Not a file handle.
    
    stream: BinaryIO = STREAMS[handle]
    
    if stream is None:
        return False # File already closed.
    
    stream.close()
    STREAMS[handle] = None
    return True


def get_intrinsic(arguments: list[Any]) -> float | None:
    """ The get intrinsic. """
    
    handle: int = int(arguments[0])
    
    if handle < 0 or handle >= len(STREAMS):
        return None # Invalid file handle.
    
    stream: BinaryIO | None = STREAMS[handle]
    
    if stream is None:
        return None # Unopened stream.
    
    try:
        result: bytes = stream.read(1)
    except (OSError, ValueError):
        return None # Failed to get byte.
    
    if not result:
        return None # End of file.
    
    return float(result[0])


def length_intrinsic(arguments: list[Any]) -> float:
    """ The length intrinsic. """
    
    return float(len(str(arguments[0])))


def ord_intrinsic(arguments: list[Any]) -> float | None:
    """ The ord intrinsic. """
    
    character: str = str(arguments[0])
    
    if len(character) != 1:
        return None # Not a single character.
    
    code: int = ord(character)
    
    if code < 0 or code > 255:
        return None # Not an ASCII character.
    
    return float(code)


def put_intrinsic(arguments: list[Any]) -> float | None:
    """ The put intrinsic. """
    
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


def read_intrinsic(arguments: list[Any]) -> float | None:
    """ The read intrinsic. """
    
    return open_file_handle(str(arguments[0]), "rb")


def stderr_intrinsic(arguments: list[Any]) -> float:
    """ The stderr intrinsic. """
    
    return 2.0


def stdin_intrinsic(arguments: list[Any]) -> float:
    """ The stdin intrinsic. """
    
    return 0.0


def stdout_intrinsic(arguments: list[Any]) -> float:
    """ The stdout intrinsic. """
    
    return 1.0


def substring_intrinsic(arguments: list[Any]) -> str | None:
    """ The substring intrinsic. """
    
    string: str = str(arguments[0])
    start: int = int(arguments[1])
    end: int = start + int(arguments[2])
    
    if start < 0 or end < start or end > len(string):
        return None # Substring out of bounds.
    
    return string[start:end]


def write_intrinsic(arguments: list[Any]) -> float | None:
    """ The write intrinsic. """
    
    return open_file_handle(str(arguments[0]), "wb")


def trunc_intrinsic(arguments: list[Any]) -> float:
    """ The trunc intrinsic. """
    
    return float(math.trunc(float(arguments[0])))


def open_file_handle(path: str, mode: str) -> float | None:
    """ Open and return a new file handle from a path and a mode. """
    
    handle: int = FILE_HANDLE_MIN
    
    while handle < len(STREAMS):
        if STREAMS[handle] is None:
            try:
                stream: BinaryIO = open(path, mode)
                STREAMS[handle] = stream
                return float(handle)
            except OSError:
                return None # Failed to open file handle.
        
        handle = handle + 1
    
    return None # No file handles available.


def install_intrinsics(
        define_native: Callable[
                [str, int, Callable[[list[Any]], Any]], None]) -> None:
    """ Install the intrinsics. """
    
    define_native("_argc", 1, argc_intrinsic)
    define_native("_argv", 0, argv_intrinsic)
    define_native("_chr", 1, chr_intrinsic)
    define_native("_close", 1, close_intrinsic)
    define_native("_get", 1, get_intrinsic)
    define_native("_length", 1, length_intrinsic)
    define_native("_ord", 1, ord_intrinsic)
    define_native("_put", 2, put_intrinsic)
    define_native("_read", 1, read_intrinsic)
    define_native("_stderr", 0, stderr_intrinsic)
    define_native("_stdin", 0, stdin_intrinsic)
    define_native("_stdout", 0, stdout_intrinsic)
    define_native("_substring", 3, substring_intrinsic)
    define_native("_trunc", 1, trunc_intrinsic)
    define_native("_write", 1, write_intrinsic)
