#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Sentinel:
    pass
null = Sentinel()
class FixedSizeDict(dict):
    def __init__(self,size):
        self._key=[ null ] * size
        self._cursor=0
        self._size=size
        dict.__init__({})

    def __setitem__(self,key, value):
        self._cursor +=1
        self._cursor %= self._size
        if self._key[self._cursor] is not null:
            del self[self._key[self._cursor]]
        self._key[self._cursor]=key
        dict.__setitem__(self, key,value)

    def update(self,*a,**kw):
        raise Exception("This shall not pass")

