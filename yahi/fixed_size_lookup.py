#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fixed size lookup table. 
A looklup table is like a dict except that if you want to 
update or set an already existing value, it blows up"""

class SafeGuard:
    """guarding all entry point we don't want to be visited"""
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
        
__all__=[ 'FixedLookupTable' ]

SENTINEL = object()
### my pityfully lame implementation
class jtFixedLookupTable(dict,SafeGuard):
    def __init__(self,size):
        self._key=array([ SENTINEL ] * size)
        self._cursor=0
        self._size=size
        dict.__init__({})

    def __setitem__(self,key, value):
        self._cursor +=1
        self._cursor %= self._size
        if self._key[self._cursor] is not SENTINEL:
            dict.__delitem__(self,self._key[self._cursor])
        self._key[self._cursor]=key
        dict.__setitem__(self,key,value)


from collections import deque
### bmispelon implementation appearing by courtesy
class FixedLookupTable(dict,SafeGuard):
    """a circular dict of a fixed size : 
    if size is greater than its upper bound, new key will replace the older
    This is *NOT* a LRU cache. This is a FIFO cache
    """

    def __init__(self, maxsize):
        self._keys = deque([SENTINEL] * maxsize)
        self.maxsize = maxsize
        dict.__init__({})
        # TODO: trim the fat (maybe using dict.popitem)
    
    def __setitem__(self, key, value):
        oldkey = self._keys.popleft()
        if oldkey is not SENTINEL:
        #    print oldkey in self._keys
            dict.__delitem__(self,oldkey)
        self._keys.append(key)
        dict.__setitem__(self,key,value)

bmFixedLookupTable = FixedLookupTable
