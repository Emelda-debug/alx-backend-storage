#!/usr/bin/env python3
"""
requests module to obtain the HTML content of a particular URL and returns it.
"""
import redis
import requests
from functools import wraps
from typing import Callable


def track_get_page(fn: Callable) -> Callable:
    """ Decorator for the get_page """
    @wraps(fn)
    def output_cacher(url: str) -> str:
        """ Wrapper to check if a url's data is cached and
        tracks how many times get_page is called
        """
        cache_client = redis.Redis()
        cache_client.incr(f'count:{url}')
        cached_page = cache_client.get(f'{url}')
        if cached_page:
            return cached_page.decode('utf-8')
        cache_client.set(f'{url}', fn(url), 10)
        return fn(url)
    return output_cacher


@track_get_page
def get_page(url: str) -> str:
    """tracks request and returns it;s URL's contents after caching its respnse"""
    return requests.get(url).text
