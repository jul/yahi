Using the console requesting a log like a boss
==============================================

For this exercice I do have a preference for *bpython*, since it has the ctrl+S shortcut.  Thus, you can save any «experiments» in a file. 

It is pretty much a querying language in disguise. 

Notch and shoot by the example
==============================


notch is setting up a one time context::
    
     context=notch(
         'yahi/test/biggersample.log', 
         'yahi/test/biggersample.log',
         include="yahi/test/include.json",
                             silent=True, 
                                                                 exclude='{ "country" : "US"}', 
                                                                             output_format="csv"
                                                                                     )




