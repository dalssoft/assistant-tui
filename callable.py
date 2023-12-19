import inspect
import asyncio


class Callable:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        if inspect.iscoroutinefunction(self.fn):
            asyncio.ensure_future(self.fn(*args, **kwargs))
        else:
            self.fn(*args, **kwargs)
