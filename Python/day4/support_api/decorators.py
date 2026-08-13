"""
Decorators:
    wrap around an existing function and change how they operate
    decorator function takes in another functin as its param

    functools
        functools.wraps(func)
            create the wrapper that alters the original function
            preserves identity of original function
                metadata, docstrings
"""

import functools
import time
import logging

# giving ourselves a logger for this context
logger = logging.getLogger(__name__)

def shout(func):

    """
        without @functools.wraps(), the original function will take on the identity of wrapper

        this function DOES NOT use it and then filter_tickets() thinks it is named "wrapper"

        best practice: always use @functools.wraps()
    """

    def wrapper(*args, **kwargs):
        logger.info("positional arguments: %s", args)
        logger.info("keyword arguments: %s", kwargs)

        message = f"calling {func.__name__}"
        logger.warning(message.upper())

        return func(*args, **kwargs)

    return wrapper

def timed(func):

    """ decorator function to time the completion of a function """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__} took {elapsed} seconds")
        return result

    # make sure to return the wrapper we created
    return wrapper