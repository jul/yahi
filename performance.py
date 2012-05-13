from functools import wraps

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
