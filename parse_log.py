#!/usr/bin/env python
from datetime import datetime as dt
import httpagentparser
from itertools import ifilter, imap
from json import dumps
from pygeoip import GeoIP
import re
from vector_dict.VectorDict import VectorDict as krut, convert_tree as kruter


LOG_LINE_REGEXP = re.compile(
'''^(?P<ip>\S+?)\s # ip
-\s                    # dunno
(?P<user>[^ ]+)\s      # if authentified
\[(?P<time>[^\]]+)\]\s # apache format
"(?P<method>[A-Z]+)\   # GET/POST/....
(?P<uri>[^ ]+)\        # add query it would be nice
HTTP/1.\d"\            # whole scheme (catching FTP ... would be nicer)
(?P<status>\d+)\       # 404 ...
(?P<bytes>\d+)\        # bytes really bite me if you can
"(?P<referer>[^"]+)"\  # where people come from
"(?P<agent>[^"]+)"$    # well ugly chain''', re.VERBOSE)

def memoize(cache):
    """A simple memoization decorator.
    Only functions with positional arguments are supported."""
    def decorator(fn):
        def wrapped(*args):
            cache.setdefault(args, fn(*args))
            return cache[args]
        return wrapped
    return decorator

_CACHE = {}

@memoize(_CACHE)
def normalize_user_agent(user_agent):
    default = {
        'os': {'name': "unknown", "version": 'unknown'},
        'browser': {'name': "unknown", "version": 'unknown'},
        'dist': {'name': "unknown", "version": 'unknown'},
        }
    iam = httpagentparser.detect(user_agent)
    if not iam:
        return default
    iam.setdefault("dist", default["dist"])
    return iam

def parse_log_line(line):
    """Produce a dict of the data found in the line.
    If the line is not recognized, return None.
    
    """
    match = LOG_LINE_REGEXP.search(line)
    if not match:
        return None
    data = match.groupdict()
    fdate = dt.strptime(data["time"][:-6], "%d/%b/%Y:%H:%M:%S")
    data.update({
        "date": fdate.strftime('%Y-%m-%d'),
        "time": fdate.strftime('%H:%M:%S.%f'),
        "agent_class": normalize_user_agent(data["agent"])
    })
    return data

if __name__ == '__main__':
    import fileinput
    gi = GeoIP("data/GeoIP.dat")
    
    def krutify(data):
        return krut(int, {
            "by_country": krut(int, {gi.country_code_by_addr(data['ip']): 1}),
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
            "bytes_by_ip": krut(int, {data['ip']: int(data["bytes"])})
        })
    
    def is_local(ip):
        return ip.startswith('192.168')
    
    reduce(
        krut.__add__,
        imap(krutify, ifilter(
                lambda x: not is_local(x['ip']),
                ifilter(None, imap(parse_log_line, fileinput.input()))
            )
        )
    ).tprint()
