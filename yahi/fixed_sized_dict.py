#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Sentinel:
    pass

class FixedSizeDict(dict):
    def __init__(self,size,_dict={}):
        self._null = Sentinel()
        self._key=[ self._null ] * size
        self._cursor=0
        self._size=size
        self = dict.__init__(_dict)

    def __setitem__(self,key, value):
        self._cursor +=1
        self._cursor %= self._size
        if self._key[self._cursor] != self._null:
            del self[self._key[self._cursor]]
        self._key[self._cursor]=key
        dict.__setitem__(self, key,value)

