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

def arg_extension(arguments: list[Any]) -> str | None:
    """ The arg extension. """
    
    index: int = int(arguments[0]) + 1
    
    if index < 1 or index >= len(sys.argv):
        return None # Argument out of range.
    
    return sys.argv[index]


def args_extension(arguments: list[Any]) -> float:
    """ The args extension. """
    
    return float(max(len(sys.argv) - 1, 0))


def close_extension(arguments: list[Any]) -> bool:
    """ The close extension. """
    
    handle: int = int(arguments[0])
    
    if handle < FILE_HANDLE_MIN or handle >= len(STREAMS):
        return False # Not a file handle.
    
    stream: BinaryIO = STREAMS[handle]
    
    if stream is None:
        return False # File already closed.
    
    stream.close()
    STREAMS[handle] = None
    return True


def get_extension(arguments: list[Any]) -> float | None:
    """ The get extension. """
    
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


def read_extension(arguments: list[Any]) -> float | None:
    """ The read extension. """
    
    return open_file_handle(str(arguments[0]), "rb")


def stderr_extension(arguments: list[Any]) -> float:
    """ The stderr extension. """
    
    return 2.0


def stdin_extension(arguments: list[Any]) -> float:
    """ The stdin extension. """
    
    return 0.0


def stdout_extension(arguments: list[Any]) -> float:
    """ The stdout extension. """
    
    return 1.0


def write_extension(arguments: list[Any]) -> float | None:
    """ The write extension. """
    
    return open_file_handle(str(arguments[0]), "wb")


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


def install_extensions(
        define_native: Callable[
                [str, int, Callable[[list[Any]], Any]], None]) -> None:
    """ Install the extensions. """
    
    define_native("arg", 1, arg_extension)
    define_native("args", 0, args_extension)
    define_native("close", 1, close_extension)
    define_native("get", 1, get_extension)
    define_native("put", 2, put_extension)
    define_native("read", 1, read_extension)
    define_native("stderr", 0, stderr_extension)
    define_native("stdin", 0, stdin_extension)
    define_native("stdout", 0, stdout_extension)
    define_native("write", 1, write_extension)
