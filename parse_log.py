#!/usr/bin/env python
import argparse
from datetime import datetime
import fileinput
from fnmatch import fnmatch
import httpagentparser
from itertools import ifilter, imap
from json import dumps
from pygeoip import GeoIP
import re
import sys
from vector_dict.VectorDict import VectorDict as krut

HARDCODED_GEOIP_FILE = "data/GeoIP.dat"

LOG_LINE_REGEXP = re.compile(
'''^(?P<ip>\S+?)\s            # ip
-\s                           # dunno
(?P<user>[^ ]+)\s             # if authentified
\[(?P<datetime>[^\]]+)\s      # apache format
(?P<tz_offset>[+-]\d{4})\]\s  #
"(?P<method>[A-Z]+)\          # GET/POST/....
(?P<uri>[^ ]+)\               # add query it would be nice
HTTP/1.\d"\                   # whole scheme (catching FTP ... would be nicer)
(?P<status>\d+)\              # 404 ...
(?P<bytes>\d+)\               # bytes really bite me if you can
"(?P<referer>[^"]+)"\         # where people come from
"(?P<agent>[^"]+)"$           # well ugly chain''', re.VERBOSE)

def memoize(cache):
    """A simple memoization decorator.
    Only functions with positional arguments are supported."""
    def decorator(fn):
        def wrapped(*args):
            cache.setdefault(args, fn(*args))
            return cache[args]
        return wrapped
    return decorator

_CACHE_UA = {}
_CACHE_GEOIP = {}

@memoize(_CACHE_UA)
def normalize_user_agent(user_agent):
    iam= {
        'os': {'name': "unknown", "version": 'unknown'},
        'browser': {'name': "unknown", "version": 'unknown'},
        'dist': {'name': "unknown", "version": 'unknown'},
        }.update(httpagentparser.detect(user_agent))
    return iam

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

excluding IPs (10/8 and 192.168/16)
***********************************
parse_log -x "10.*" -x "192.168.*"  /var/log/apache.log  > dat2.json

Since VectorDict is cool here is a tip for aggregating data
>>> from vector_dict.VectorDict import convert_tree as kruter
>>> from json import load, dumps
>>> dumps(kruter(load(file("dat1.json"))) + kruter(load(file("dat2.json"))))

Hence a usefull trick to merge your old stats with your new one
        """
         )
         
    parser.add_argument("-g",
        "--geoip",
        help="specify a path to a geoip.dat file",
        metavar="FILE",
        default=HARDCODED_GEOIP_FILE
    )
    parser.add_argument("-x",
        "--exclude-ip",
        help="exclude an IP address (wildcards accepted)",
        action="append"
    )
    parser.add_argument("-O",
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
    
    gi = GeoIP(args.geoip)
    country_by_ip = memoize(_CACHE_GEOIP)(gi.country_code_by_addr)
    
    
    def krutify(data):
        return krut(int, {
            "by_country": krut(int, {country_by_ip(data['ip']): 1}),
            "by_date": krut(int, {data["date"]: 1 }),
            "by_hour": krut(int, {data["time"][0:2]: 1 }),
            "by_os": krut(int, {data["agent_class"]['os']['name']: 1 }),
            "by_dist": krut(int, {data["agent_class"]['dist']['name']: 1 }),
            "by_browser": krut(int, {data["agent_class"]['browser']['name']: 1 }),
            "by_ip": krut(int, {data['ip']: 1 }),
            "by_status": krut(int, {data['status']: 1 }),
            "by_url": krut(int, {data['uri']: 1}),
            "by_agent": krut(int, {data['agent']: 1}),
            "ip_by_url": krut(int, {data['uri']: krut (int, {data['ip']: 1 })}),
            "bytes_by_ip": krut(int, {data['ip']: int(data["bytes"])}),
            "total_line" : 1,
        })
    
    def filter_ip(data):
        if not data:
            return False
        if not args.exclude_ip:
            return True
        return not any(fnmatch(data["ip"], glob) for glob in args.exclude_ip)
    
    args.output_file.write(dumps(
        reduce(
            krut.__add__,
            imap(krutify, ifilter(
                    filter_ip,
                    imap(parse_log_line, fileinput.input(args.files))
                )
            )
        ),
        indent=4
    ))
