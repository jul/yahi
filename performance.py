from functools import wraps
import sys


def memoize(cache):
    """A simple memoization decorator.
    Only functions with positional arguments are supported."""
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args):
            if args not in cache:
                cache[args] = fn(*args)
            return cache[args]
        return wrapped
    return decorator

def print_res(what, ok_or_ko,fn):
    """prints rejected lines"""
    @wraps(fn)
    def wrapped(*a):
        res = fn(*a)
        if res == ok_or_ko:
            sys.stderr.write( "\n%s:%s %s" % (res and "OK" or "KO",what,a))
        return res
    return wrapped


