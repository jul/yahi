How it works?
*************

Notch: setting up a context
===========================


notch is all about setting up a context::
    >>> context = notch(
         'yahi/test/biggersample.log', 
         include="yahi/test/include.json",
         silent=True, 
         exclude='{ "_country" : "US"}', 
         output_format="csv"
    )

It defines the parameter for your parsing and the target.


Command line arguments vs notch arguments
=========================================


- first command lines arguments are parsed, and setup;
- then the arguments of `notch` are parsed. 

.. warning:: notch arguments always override arguments given in the 
   command line. 


Context methods & attributes
============================

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
        - add to record datetime string in **_datetime** key

          if **geoIP** in **context.skill**
            add *_country* to the record bades on *ip*
          if **user_agent** in **context.skill**
            add *_dist_name*, *_browser_version*, *_browser_version* on *agent* 
          if not filtered out by context.data_filter
            add actual transformed record to the previous one

It is basically a way to **GROUP BY** like in mysql.
As my dict supports addition we have the following logic for each line (given 
you request an aggregation on country and useragent and you are at the 31st line::

    >>> { '_country' : { 'BE' : 10, 'FR' : 20  
    ... },  'user_agent' : { 'mozilla' : 13, 'unknown' : 17  } } + { 
    ... 'country' : { 'BE' : 1}, 'user_agent' : { 'safari': 1 } }
    { '_country' : { 'BE' : 11, 'FR' : 20 },
    'user_agent' : { 'mozilla' : 13, 'unknown' : 17,'safari': 1 } }
    },

How lines of your log are transformed
=====================================

First since we use named capture in our log regexps, we directly transform 
a log in a dict. You can give the name you want for your capture except for
3 special things: 

- *datetime* is required, because logs **always** have a datetime associated with each record;
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



