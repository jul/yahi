Notch and shoot logic
*********************

For this exercice I do have a preference for *bpython*, since it has the ctrl+S shortcut.  Thus, you can save any «experiments» in a file. 

It is pretty much a querying language in disguise. 

Initially I did not planned to use it in a console or as a standalone module
so the API is not satisfying. 

Notch and shoot by the example
==============================

So let's take an example::
    >>> context=notch( 
         'yahi/test/biggersample.log' ,'another_log', 
         include="yahi/test/include.json",
         exclude='{ "ip" : "^(192\.168|10\.)"}', 
         output_format="csv"
    )
    # include.json contains : { "_country"  : "GB","user" : "-" }

Here you parse two files, you want: 

- only GB hits,
- non authed users,
- to filter out private IP, 
- and you may want to use a CSV formater as an output format.

(Since no output file is set, output is redirected to stdout (errors are directed 
on stderr)). 


Shoot: choose and aggregate your data
=====================================

Shoot has 2 inputs:

- a context (setup by notch);
- an extractor;

Ad extractor is a function extracting and transforming datas, and since I love
short circuits, that may contain some on the fly filtering :) 

Total hits in a log matching the conditions from notch
------------------------------------------------------

Example::
    >>> from archery import Hankyu as _dict
    >>> shoot( 
    ... context,
    ... lambda data: _dict({ 'total_lines' : 1 }) 
    ... )


Gross total hits in business hours and off business hour
--------------------------------------------------------

Business hour being each weekday from monday to friday, between 8 am and 5 pm.

Example::
    >>> from archery import Hankyu as _dict
    >>> shoot( 
    ... context,
    ... lambda data: _dict({ ( 
    ...        8 >= data["_datetime"].hour >= 17 and 
    ...        data["_datetime"].weekday() < 5 
    ...    ) and "business_hour" or "other_hour" :  1 }) 
    ... )

Hankyu is a dict supporting addition.

Distinct IP
-----------


Example::
    >>> from archery import Hankyu as _dict
    >>> from yahi import ToxicSet
    >>> shoot( 
    ... context,
    ... lambda data: _dict(distinct_ip = ToxicSet({ data["ip"]}))
    ... )

ToxicSet is a set that maps add to union.

Hits per day
------------
example:: 
    >>> date_formater= lambda dt :"%s-%s-%s" % ( dt.year, dt.month, dt.day)
    >>> from archery import Hankyu as _dict
    >>> shoot( 
    ... context,
    ... lambda data: _dict({ 
    ...     date_formater(data["_datetime"]) : 1 
    ... })




































