#!/usr/bin/env python
import argparse
from datetime import datetime
import fileinput
import fnmatch
from os import path
import httpagentparser
from itertools import ifilter, imap
from json import dumps
from pygeoip import GeoIP
import re
import sys
from json import load, loads
from performance import memoize, print_res
from archery.bow import Hankyu
from archery.barrack import mapping_row_iter

HARDCODED_GEOIP_FILE = "data/GeoIP.dat"

LOG_LINE_REGEXP = re.compile(
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
"(?P<agent>[^"]+)"$           # well ugly chain''', re.VERBOSE)


_CACHE_UA = {}
_CACHE_GEOIP = {}

@memoize(_CACHE_UA)
def normalize_user_agent(user_agent):
    deft = {
        'os': {'name': "unknown", "version": 'unknown'},
        'browser': {'name': "unknown", "version": 'unknown'},
        'dist': {'name': "unknown", "version": 'unknown'},
        }
    deft.update( httpagentparser.detect(user_agent) )
    return deft 

def parse_date(s):
    """Transform the datetime string from the log into an actual datetime object."""
    return datetime.strptime(s, "%d/%b/%Y:%H:%M:%S")

def parse_log_line(line):
    """Produce a dict of the data found in the line.
    If the line is not recognized, return None.
    
    """
    match = LOG_LINE_REGEXP.search(line)
    if not match:
        return None
    data = match.groupdict()
    fdate = parse_date(data["datetime"])
    data.update({
        "date": fdate.strftime('%Y-%m-%d'),
        "time": fdate.strftime('%H:%M:%S.%f'),
        "agent_class": normalize_user_agent(data["agent"])
    })
    return data

def get_parser():
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
            list of comma separated stuff to diagnose :
                * rejected : will print on STDERR rejected parsed line
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

    parser.add_argument("-o",
        "--output-file",
        help="output file",
        nargs='?',
        type=argparse.FileType('w'),
        default=sys.stdout
    )
    parser.add_argument('files', nargs=argparse.REMAINDER)
    
    return parser

if __name__ == '__main__':
    parser = get_parser()
    
    args = parser.parse_args()
    if args.config:
        config_args = load(open(args.config))
        for k in config_args:
            if not getattr(args,k):
                setattr(args, k, config_args[k])

    gi = GeoIP(args.geoip)
    country_by_ip = memoize(_CACHE_GEOIP)(gi.country_code_by_addr)
    
    
    def emit(data):
        return Hankyu({
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
        
    _data_filter = lambda data : True if data else False
    if args.exclude:
        str_or_file=args.exclude
        matcher = {}
        try:
            matcher.update(str_or_file)
        except TypeError: 
                matcher = load(open(str_or_file))
        except ValueError:
            ## errno 2 <=> file not found
            matcher =  loads(str_or_file)
        

        if len(matcher):
            for field, regexp in matcher.items():
                matcher[field] = re.compile(regexp).match
            
            _data_filter = lambda data : not(any(matcher[k](data[k]) for k in matcher)
                ) if data else False
    if "rejected" in args.diagnose:
        _data_filter =  print_res("REJECTED",False,_data_filter)

    if "match" in  args.diagnose:
        parse_log_line = print_res("NOT MATCHED",None, parse_log_line) 

    if "csv" == args.output_format:
        import csv
        output = lambda out,aggreg : csv.writer(out).writerows(
            mapping_row_iter(aggreg))
    else:
        output = lambda out,aggreg : out.write(dumps(aggreg,indent=4))
    
    output(
        args.output_file,
        reduce(
            Hankyu.__iadd__,
            imap(emit, ifilter(
                    _data_filter,
                    imap(parse_log_line, fileinput.input(args.files))
                )
            )
        )
    )
