How it works?
*************

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

Here you parse two files, you will want to get only GB hits of non authed users,except private IP, and you may want to sue CSV as an output format. (Since 
no output file is set, output is redirected to stdout (errors are directed 
on stderr). 

Shoot
=====

Let's get a time serie of the hit per day and 


Context methods & attributes
============================

Initially this code was written in pure map reduce unreadable style. 
Then, I noticed that a `for lines in files` was quite faster. 

Code was first a 100 lines script then it grew out of control.


attribute: data_filter
-----------------------

Stores the filter used to filter the data. If nothing specified it will
use include and exclude. 

method: output
--------------

Given output_file / output_format write a Mapping in the specified 
file with the sepcified format. 


.. warning:: 
    Output will close output_file once it has written in it.
    Thus, reusing it another time will cause an exception. 
    you should notch once for every time you shoot if you `context.output`
    for writing to a file. 
    

Shoot
=====

Logic
-----

Given one or more context, you now can shoot your request to the context
given back by notch. 

.. note::
    for each lines of each input file
        - use a regexp to transform the parsed line in a dict
        - add to record datetime string in _datetime key
        if geoIP in context.skill
            add country to the record
        if user_agent in context.skill
            add os / dist / browser to the record based on the agent record 
        if not filtered out by context.data_filter
            add actual transformed record to the previous one

It is basically a way to **GROUP BY** like in mysql.
As my dict supports addition we have the following logic for each line (given 
you request an aggregation on country and useragent and you are at the 31st line::
    >>> { '_country' : { 'BE' : 10, 'FR' : 20  
    ... },  'user_agent' : { 'mozilla' : 13, 'unknown' : 17  } } + { 
    ... '_country' : { 'BE' : 1}, 'user_agent' : { 'safari': 1 } }
    { '_country' : { 'BE' : 11, 'FR' : 20 },
    'user_agent' : { 'mozilla' : 13, 'unknown' : 17,'safari': 1 } }
    },

How lines of your log are transformed
=====================================

First since we use named capture in our log regexps, we directly transform 
a log in a dict. You can give the name you want for your capture except for
3 special things: 

- *datetime* is required, because logs **always** have a datetime associated
with each record;
- *agent* is required if you want to use **httpagentparser**;
- *ip* is required if you want to use **geoIP**

Datetime
--------

Once *datetime* is captured since datetime objects are easier to use than strings
`datetime` value is  transformed in `_datetime` with the date_pattern.

GeoIP
-----

Once *ip* is catpured given `geo_ip` is enabled `_country` will be set with
the 2 letters of the ISO code of the country.

HttpUserAgentParser
-------------------

Once agent is captured, it will be transformed -if `user_agent` is enabled- into

- `_dist_name`: the OS;
- `_browser_name`: the name of the web browser;
- `_browser_version`: the version of the browser.



