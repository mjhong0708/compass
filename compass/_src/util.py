import functools
import inspect


def check_installed(module):
    try:
        __import__(module)
    except ImportError:
        print("{} not found. Please install {}.".format(module, module))
        raise
    del module


def humanize_bytes(n: int, precision: int = 2) -> str:
    # Author: Doug Latornell
    # Licence: MIT
    # URL: https://code.activestate.com/recipes/577081/
    # Re-copied from: https://github.com/httpie/httpie/
    """Return a humanized string representation of a number of bytes.
    >>> humanize_bytes(1)
    '1 B'
    >>> humanize_bytes(1024, precision=1)
    '1.0 kB'
    >>> humanize_bytes(1024 * 123, precision=1)
    '123.0 kB'
    >>> humanize_bytes(1024 * 12342, precision=1)
    '12.1 MB'
    >>> humanize_bytes(1024 * 12342, precision=2)
    '12.05 MB'
    >>> humanize_bytes(1024 * 1234, precision=2)
    '1.21 MB'
    >>> humanize_bytes(1024 * 1234 * 1111, precision=2)
    '1.31 GB'
    >>> humanize_bytes(1024 * 1234 * 1111, precision=1)
    '1.3 GB'
    """
    abbrevs = [(1 << 50, "PB"), (1 << 40, "TB"), (1 << 30, "GB"), (1 << 20, "MB"), (1 << 10, "kB"), (1, "B")]

    if n == 1:
        return "1 B"

    for factor, suffix in abbrevs:
        if n >= factor:
            break

    # noinspection PyUnboundLocalVariable
    return f"{n / factor:.{precision}f} {suffix}"


def notice_available_args(exclude: list = None):

    """Decorator to print available arguments for a function.
    Args:
        fn (callable): Function to print available arguments
    """
    if exclude is None:
        exclude = []

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except TypeError as e:
                avail_args = inspect.signature(fn).parameters.keys()
                avail_args = [arg for arg in avail_args if arg not in exclude]
                raise TypeError(f"{e}. Available arguments: {avail_args}")

        return wrapper

    return decorator
