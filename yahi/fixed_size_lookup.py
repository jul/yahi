#!/usr/bin/env python
# -*- coding: utf-8 -*-
class SafeGuard:
    def pop(self,*a,**kw):
        raise Exception("Unsafe Method")

    def popitem(self,*a,**kw):
        raise Exception("Unsafe Method")

    def update(self,*a,**kw):
        raise Exception("Unsafe Method")

    def clear(self,*a,**kw):
        raise Exception("Unsafe Method")

    def setdefault(self,*a,**kw):
        raise Exception("Unsafe Method")
        


class Sentinel:
    pass
NULL = Sentinel()

class FixedLookupTable(SafeGuard):
    def __init__(self,size, factory=dict):
        self._key=[ NULL ] * size
        self._cursor=0
        self._size=size
        factory.__init__({})

    def __setitem__(self,key, value):
        self._cursor +=1
        self._cursor %= self._size
        if self._key[self._cursor] is not NULL:
            del self[self._key[self._cursor]]
        self._key[self._cursor]=key
        dict.__setitem__(self, key,value)


from collections import deque
class bmFixedLookupTable(SafeGuard):
    def __init__(self, maxsize, factory =dict):
        self._keys = deque([SENTINEL] * maxsize)
        self.maxsize = maxsize
        factory.__init__({})
        # TODO: trim the fat (maybe using dict.popitem)

    def __setitem__(self, key, value):
        oldkey = self._keys.pop(0)
        if oldkey is not SENTINEL:
            del self[oldkey]
        self._keys.append(key)
        self[key] = value
