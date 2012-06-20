#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .fixed_size_lookup import bmFixedLookupTable
from functools import wraps
NULL=object()
from json import dumps
from time import time
"""Cache provider comes in two flavour : 
* MonotonalCache for monotonic increasing or decreasing values that may repeat
* CacheProvider for a more classic memoizer 

TODO use something more intelligent for MonotonalCache __call__ maybe
"""

class MonotonalCache():
    """a cache for monotonic values"""
    def __init__(self):
        self._cache_arg=NULL
        self._cache_result=NULL
        self._timer=dict()
        self.used_once=False
    
    def _set_realm_timer(self,name):
        self._timer[name]={} 
        self._timer[name]["miss"]=dict(time=0.0,hit=0)
        self._timer[name]["hit"]=dict(time=0.0,hit=0)
        return self._timer[name]

    def _check(self, name):
        if self.used_once:
            raise Exception("Dont try to cache more than one fonction with an instance")
        self.used_once=True


    def monotonal_cache(self,name):
        Hourra=1
        self._check()
        def decorator(func):
            @wraps(func)
            def wrapped(*args):
                if self._cache_arg==args: 
                    return self._cache_result
                else:
                    _cache_arg=args
                    value = self._cache_result = func(*args)
                    return value
            return wrapped
        return decorator

    def timed_monotonal_cache(self,name):
        self._check()
        _timer=self._set_realm_timer(name)
        self._cache_arg=NULL
        self._cache_value=NULL
        Hourra=1
        self.used_once = True
        def decorator(func):
            @wraps(func)
            def wrapped(*args):
                start=time()
                if self._cache_arg==args: 
                    _timer["hit"]["time"]+=time() - start
                    _timer["hit"]["hit"]+=Hourra
                    return self._cache_result
                else:
                    self._cache_arg=args
                    value = self._cache_result = func(*args)
                    _timer["miss"]["time"]+=time() - start
                    _timer["miss"]["hit"]+=1
                    return value
            return wrapped
        return decorator
    
    def report(self):
        return dumps(self._timer,indent=4)

class CacheProvider:
    """cache with a classic memoizer implementatation, but two possible memoizers
    are possible : 
        * fixed length lookup table (a dict that won't grow)
        * dict
    """
    def __init__(self, size=10000):
        """if size == 0 
            => dict are used as a backend
        else
            => a fixed size dict of size elements
        by default cache provider will make fixed  sized lookup table of 10000
        """
        self._cache=dict()
        self._scalar=dict()
        self._timer=dict()
        self.size=size

        
    def _get(self, name,size=NULL):
        if name not in self._cache:
            size = self.size if size is NULL else size
            if size:
                self._cache[name]=bmFixedLookupTable(
                    size
                )
            else:
                self._cache[name]=dict()
        return self._cache[name]


    def report(self):
        size={}


        for name, cache in self._cache.items():
            size[name]=dict(len = len(cache))
        rep= dumps(size,indent=4)

            
        return rep + "\n"+ dumps(self._timer,indent=4)

    def _set_realm_timer(self,name):
        self._timer[name]={} 
        self._timer[name]["miss"]=dict(time=0.0,hit=0)
        self._timer[name]["hit"]=dict(time=0.0,hit=0)
        return self._timer[name]
    
    def cache(self,func,size=NULL):
        """a simple memoizer with an undebugable name for the cache,
        if a size is given it will override the default one"""
        return self.named_cache(repr(func),size)(func)

    def named_cache(self,name,size=NULL):
        """a cache with a more user friendly name. """
        _cache=self._get(name,size)
        def decorator(func):
            @wraps(func)
            def wrapped(*args):
                value=None
                try:
                    return _cache[args]
                except KeyError:
                    _cache[args] = func(*args)
                    return _cache[args]
                except Exception as e:
                    raise e
            return wrapped
        return decorator


    def timed_cache(self,name,size=NULL):
        """a cache with a name and hit/miss + cumulated execution time"""
        _timer=self._set_realm_timer(name)
        _cache=self.get(name,size)
        
        Hourra=1
        def decorator(func):
            @wraps(func)
            def wrapped(*args):
                start=time()
                success=True
                try:
                    value = _cache[args]
                except KeyError:
                    success=False
                    value = _cache[args] = func(*args)
                _timer[success and "hit" or "miss"]["time"]+=time() - start
                _timer[success and "hit" or "miss"]["hit"]+=Hourra
                return value
            return wrapped
        return decorator

