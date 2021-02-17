class Dispatch:
    def __init__(self):
        self.lookup = {}

    def register(self, key, fn=None):
        def wrapper(fn):
            self.lookup[key] = fn

            return fn

        return wrapper(fn) if fn is not None else wrapper

    def __call__(self, key, *args, **kwargs):
        try:
            fn = self.lookup[key]
        except KeyError:
            raise ValueError("%s not registered on the dispatcher" % key)
        else:
            return fn(*args, **kwargs)
