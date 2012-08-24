Using the console requesting a log like a boss
**********************************************

For this exercice I do have a preference for *bpython*, since it has the ctrl+S shortcut.  Thus, you can save any «experiments» in a file. 

It is pretty much a querying language in disguise. 

Initially I did not planned to use it in a console or as a standalone module
so the API is not satisfying. 

Notch and shoot by the example
==============================


notch is all about setting up a context::
    >>> context=notch(
         'yahi/test/biggersample.log', 
         'yahi/test/biggersample.log',
         include="yahi/test/include.json",
         silent=True, 
         exclude='{ "country" : "US"}', 
         output_format="csv"
    )

Would I have been smart, it would have been called «aim». Since you tell 
your target, and the parameters of your parsing (log_format...). 

Context methods & attributes
============================

Initially this code was written in pure map reduce unreadable style. 
Then, I noticed that a `for lines in files` was quite faster. 

Code was first a 100 lines script then it grew out of control.

..warning:: you should notch once for every time you shoot. 
    

attributes safely modifyable after notch is called
--------------------------------------------------

data_filter
^^^^^^^^^^^

Stores the filter used to filter the data. If nothing specified it will
use include and exclude. 

methods
-------

output
^^^^^^

Given output_file / output_format write a Mapping in the specified 
file with the sepcified format. 

..caution::
    If it is a file, output will close it. And reusing it another time
    will cause an exception. 


Shoot
=====

Logic
-----

Given one or more context, you now can shoot your request to the context
given back by notch. 

Here how it goes::
    for each lines of each input file
        use a regexp to transform the parsed line in a dict
        add to record datetime string in _datetime key
        if geoIP in context.skill
            add country to the record
        if user_agent in context.skill
            add os / dist / browser to the record based on the agent record 
        if not filtered out by context.data_filter
            add actual transformed record to the previous one

It is basically a way to **GROUP BY** like in mysql.
As my dict supports addition we have the following logic for each line (given 
you request an aggregation on country and useragent and you are at the 31st line::
    >>> { 'country' : { 'BE' : 10, 'FR' : 20  
    ... },  'user_agent' : { 'mozilla' : 13, 'unknown' : 17  } } + { 
    ... 'country' : { 'BE' : 1}, 'user_agent' : { 'safari': 1 } }
    { 'country' : { 'BE' : 11, 'FR' : 20 },
    'user_agent' : { 'mozilla' : 13, 'unknown' : 17,'safari': 1 } }
    },






