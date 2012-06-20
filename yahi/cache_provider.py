#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .fixed_size_lookup import bmFixedLookupTable
from functools import wraps
NULL=object()
from json import dumps
from time import time


class MonotonalCache():
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
    def named_cache(self, name):
        if self.used_once:
            raise Exception("Dont try to cache more than one fonction with an instance")


    def monotonal_cache(self,name):
        Hourra=1
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
        _timer=self._set_realm_timer(name)
        self._cache_arg=NULL
        self._cache_value=NULL
        Hourra=1
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
    def __init__(self, size=100):
        self._cache=dict()
        self._scalar=dict()
        self._timer=dict()
        self.size=size

        
    def get(self, name,size=NULL):
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

            
        return rep+ dumps(self._timer,indent=4)

    def _set_realm_timer(self,name):
        self._timer[name]={} 
        self._timer[name]["miss"]=dict(time=0.0,hit=0)
        self._timer[name]["hit"]=dict(time=0.0,hit=0)
        return self._timer[name]
    
    def cache(self,func,size=NULL):
        return self.named_cache(repr(func),size)(func)

    def named_cache(self,name,size=NULL):
        _cache=self.get(name,size)
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

