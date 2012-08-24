Basic usage: command line
=========================

help as usual is obtained this way::

    ./speed_shoot --help

it spits out:

.. literalinclude:: cli_arg.txt

A commented jumbo command line example
**************************************
The following command line::

    ./speed_shoot -g data/GeoIP.dat -lf lighttpd -x '{ "datetime" : "^01/May", "uri" : "(.*munin|.*(png|jpg))$"}' -d rejected -d match -i '{ "country" : "(DE|GB)"  }' *log  yahi/test/biggersample.log 

does:

- locate  geoIP *g* file in data/GeoIP.dat;
- set log format *lf* to lighttpd;
- exclude (*x*) any match of either 
    - an uri containing munin or ending by jpg or png
    - May the first;
- include (*i*) all match containing
    - any IP which has been geoloclaized,
    - any non authentified user;
- will diagnose (*d*) (thus print on stderr) any lines that would not match
the log format regexp or any lines rejected by *-x* and  *-i*

for all the given log files.

Using a config file
*******************

Well, not impressive:: 

    ./speed_shoot -c config.json 

If any option is specified in the config file it will override those setted
in the command line.

Here is a sample of a config file:: 

    {
        "exclude" : { 
            "uri"  : ".*munin.*", 
            "referer" : ".*(munin|php).*" 
        },
        "include" : { "datetime" : "^04" },
        "silent" : "False",
        "files" : [ "yahi/test/biggersample.log" ]
    }



Easter eggs or bad idea
***********************

The following options *-x* *-i* *-c* can either take a string or a filename, 
which makes debugging of badly formatted json a pain. 


