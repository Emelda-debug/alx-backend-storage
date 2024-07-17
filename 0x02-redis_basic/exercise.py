#!/usr/bin/env python3
"""
Writing strings to Redis
"""
import redis
from functools import wraps
from uuid import uuid4
from typing import Any, Optional, Union, Callable


def count_calls(method: Callable) -> Callable:
    """ system to count how many times methods of the Cache class are called """
    @wraps(method)
    def wrapper(self: Any, *args, **kwargs) -> str:
        """  to conserve the original function’s name, docstring, etc."""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """ decorator to store the history particular function"""
    @wraps(method)
    def wrapper_function(self: *args, **kwargs) -> str:
        """method and tracks its passed argument by storingthem to redis"""
        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(f'{method.__qualname__}:outputs', output)
        return output
    return wrapper_function


def replay(fn: Callable) -> None:
    """ function to display the history of calls of a particular function"""
    client = redis.Redis()
    calls = client.get(fn.__qualname__).decode('utf-8')
    inputs = [input.decode('utf-8') for input in
              client.lrange(f'{fn.__qualname__}:inputs', 0, -1)]
    outputs = [output.decode('utf-8') for output in
               client.lrange(f'{fn.__qualname__}:outputs', 0, -1)]
    print(f'{fn.__qualname__} was called {calls} times:')
    for input, output in zip(inputs, outputs):
        print(f'{fn.__qualname__}(*{input}) -> {output}')


class Cache:
    """ defined class to cache"""

    def __init__(self) -> None:
        """ Initialization of the new cache object """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """ Stores data in redis with randomly generated key """
        key = str(uuid4())
        client = self._redis
        client.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Any:
        """ Gets and converts key's value from redis into correct data type"""
        client = self._redis
        value = client.get(key)
        if not value:
            return
        if fn is int:
            return self.get_int(value)
        if fn is str:
            return self.get_str(value)
        if callable(fn):
            return fn(value)
        return value

    def get_str(self, data: bytes) -> str:
        """ string converted from Bytes"""
        return data.decode('utf-8')

    def get_int(self, data: bytes) -> int:
        """ bytes to integers conversion"""
        return int(data)
