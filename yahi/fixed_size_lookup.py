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

class FixedLookupTable(dict,SafeGuard):
    def __init__(self,size):
        self._key=array([ NULL ] * size)
        self._cursor=0
        self._size=size
        dict.__init__({})

    def __setitem__(self,key, value):
        self._cursor +=1
        self._cursor %= self._size
        if self._key[self._cursor] is not NULL:
            dict.__delitem__(self,self._key[self._cursor])
        self._key[self._cursor]=key
        dict.__setitem__(self,key,value)


from collections import deque
class bmFixedLookupTable(dict,SafeGuard):
    def __init__(self, maxsize):
        self._keys = deque([NULL] * maxsize)
        self.maxsize = maxsize
        dict.__init__({})
        # TODO: trim the fat (maybe using dict.popitem)
    
    def __setitem__(self, key, value):
        oldkey = self._keys.popleft()
        if oldkey is not NULL:
        #    print oldkey in self._keys
            dict.__delitem__(self,oldkey)
        self._keys.append(key)
        dict.__setitem__(self,key,value)
