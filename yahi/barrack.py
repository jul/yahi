#!/usr/bin/env python
from archery.bow import Hankyu
import argparse
from datetime import datetime
import fileinput
from os import path
import httpagentparser
from json import dumps
import re
from json import load, loads
from functools import wraps
import sys


####################### STATIC DATA ################################
HARDCODED_GEOIP_FILE = "data/GeoIP.dat"
log_pattern=dict( 
    apache_log_combined = re.compile(
'''^(?P<ip>\S+?)\s            # ip
-\s                           # dunno
(?P<user>[^ ]+)\s             # if authentified
\[(?P<datetime>[^\]]+)\s      # apache format
(?P<tz_offset>[+-]\d{4})\]\s  #
"(?P<method>[A-Z]+)\          # GET/POST/....
(?P<uri>[^ ]+)\               # add query it would be nice
(?P<scheme>[A-Z]+(\/1)?).\d"\                   # whole scheme (catching FTP ... would be nicer)
(?P<status>\d+)\              # 404 ...
(?P<bytes>\d+)\               # bytes really bite me if you can
"(?P<referer>[^"]+)"\         # where people come from
"(?P<agent>[^"]+)"$           # well ugly chain''', re.VERBOSE),
    lighttpd = re.compile('''^(?P<ip>\S+?)\s            # ip
(?P<domain>[^ ]+)\s
-\s                           # dunno
\[(?P<datetime>[^\]]+)\s      # apache format
(?P<tz_offset>[+-]\d{4})\]\s  #
"(?P<method>[A-Z]+)\          # GET/POST/....
(?P<uri>[^ ]+)\               # add query it would be nice
HTTP/1.\d"\                   # whole scheme (catching FTP ... would be nicer)
(?P<status>\d+)\              # 404 ...
(?P<bytes>\d+)\               # bytes really bite me if you can
"(?P<referer>[^"]+)"\         # where people come from
"(?P<agent>[^"]+)"$           # well ugly chain''', re.VERBOSE),
)

date_format = dict( 
    apache_log_combined = "%d/%b/%Y:%H:%M:%S",
    lighttpd = "%d/%b/%Y:%H:%M:%S",
)
    


####################### UTILITIES ################################

_CACHE_DATE = {}
def date_formater(date):
    if not date in _CACHE_DATE:
        _CACHE_DATE[date]=date.strftime('%Y-%m-%d')
    return _CACHE_DATE[date]

_CACHE_UA = {}
@memoize(_CACHE_UA)
def normalize_user_agent(user_agent):
    deft = {
        'os': {'name': "unknown", "version": 'unknown'},
        'browser': {'name': "unknown", "version": 'unknown'},
        'dist': {'name': "unknown", "version": 'unknown'},
        }
    deft.update( httpagentparser.detect(user_agent) )
    return deft 



def aggregates(
        group_by,
        data_filter,
        option
        ):
    """Produce a dict of the data found in the line.
    If the line is not recognized, return None.
    
    """
    aggregator=Hankyu()
    if 'user_agent' in option.skill:
        import httpagentparser
    look_for = log_pattern[option.log_format].search
    match = None
    date_log_format = date_format[option.log_format]
    if "geo_ip" in option.skill:
        _CACHE_GEOIP = {}
        from pygeoip import GeoIP
        gi = GeoIP(option.geoip)
        country_by_ip = memoize(_CACHE_GEOIP)(gi.country_code_by_addr)


    for line in fileinput.input(option.files):
        
        match = look_for(line)
        if match:
            data = match.groupdict()
            fdate = datetime.strptime( data["datetime"], date_log_format )
            data.update({
                "date": date_formater(fdate),
                "time": fdate.strftime('%H:%M:%S.%f'),
            })
            if 'user_agent' in option.skill:
                data.update({
                    "agent_class": normalize_user_agent(data["agent"])
                })
            if data_filter and not data_filter(data):
                if "rejected" in option.diagnose:
                    sys.stderr.write("REJECTED:{0}".format(data))
            else:
                if group_by:
                   aggregator+=group_by(data)
                else:
                    aggregator+=Hankyu({
                "by_country": Hankyu({country_by_ip(data['ip']): 1}),
                "by_date": Hankyu({data["date"]: 1 }),
                "by_hour": Hankyu({data["time"][0:2]: 1 }),
                "by_os": Hankyu({data["agent_class"]['os']['name']: 1 }),
                "by_dist": Hankyu({data["agent_class"]['dist']['name']: 1 }),
                "by_browser": Hankyu({data["agent_class"]['browser']['name']: 1 }),
                "by_ip": Hankyu({data['ip']: 1 }),
                "by_status": Hankyu({data['status']: 1 }),
                "by_url": Hankyu({data['uri']: 1}),
                "by_agent": Hankyu({data['agent']: 1}),
                "by_referer": Hankyu({data['referer']: 1}),
                "ip_by_url": Hankyu({data['uri']: Hankyu( {data['ip']: 1 })}),
                "bytes_by_ip": Hankyu({data['ip']: int(data["bytes"])}),
                "total_line" : 1,
            }) 




        elif "match" in option.diagnose:
            sys.stderr.write("NOT MATCHED:{0}".format(line))
                       

#################### CLI and DOC #################################

def get_arg_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
Utility for parsing logs in the apache/nginx combined log format
and output a json of various aggregatted metrics of frequentation :
     * by Geolocation (quite fuzzy but still);
     * by user agent;
     * by hour;
     * by day;
     * by browser;
     * by status code
     * of url by ip;
     * by ip;
     * by url;
     * and bandwidth by ip;

Ok, it is pretty much a golfing contest between bmispelon and jul, and also
a proof of concept of what supporting addition in defaultdict may bring.

Example :
=========

from stdin (useful for using zcat)
**********************************
zcat /var/log/apache.log.1.gz | parse_log.py  > dat1.json

excluding IPs 192.168/16 and user agent containing Mozilla
**********************************************************
parse_log -o dat2.json -x '{ "ip" : "^192.168", "agent": "Mozill" }'  /var/log/apache*.log 

Since VectorDict is cool here is a tip for aggregating data
>>> from archery.barrack import bowyer
>>> from archery.bow import Hankyu
>>> from json import load, dumps
>>> dumps(
        bowyer(Hankyu,load(file("dat1.json"))) + 
        bowyer(Hankyu,load(file("dat2.json")))
    )

Hence a usefull trick to merge your old stats with your new one
        """
         )
    parser.add_argument("-c",
        "--config",
        help="""specify a config file in json format for the command line arguments
        any command line arguments will disable values in the config""",
        default=None
        )
    parser.add_argument("-g",
        "--geoip",
        help="specify a path to a geoip.dat file",
        metavar="FILE",
        default=HARDCODED_GEOIP_FILE
    )
    parser.add_argument("-d",
        "--diagnose",
        help="""diagnose 
            list of comma separated stuff to diagnose :\n
                * rejected : will print on STDERR rejected parsed line\n
                * match :   will print on stderr rejected matched line
        
        """,
        default=""
        
    )
    parser.add_argument("-x",
        "--exclude",
        help="""exclude from parsed line with
        a json (string or filename)""",
    )
        
    parser.add_argument("-f",
        "--output-format",
        help="decide if output is in a specified formater",
        default="json"
    )
    parser.add_argument("-lf",
        "--log-format",
        help="log format amongst apache_log_combined, lighttpd",
        default="apache_log_combined"
    )

    parser.add_argument("-o",
        "--output-file",
        help="output file",
        nargs='?',
        type=argparse.FileType('w'),
        default=sys.stdout
    )
    parser.add_argument('files', nargs=argparse.REMAINDER)
    
    return parser
