#!/usr/bin/env python
import re
from vector_dict.VectorDict import VectorDict as krut, convert_tree as kruter
from pygeoip import GeoIP
from datetime import datetime as dt
import httpagentparser
import time
gi = GeoIP("data/GeoIP.dat")

country = gi.country_code_by_addr
cache = {}
def mnemoize_detect(user_agent):
    default = {
        'os': {'name': "unknown", "version": 'unknown'},
        'browser': {'name': "unknown", "version": 'unknown'},
        'dist': {'name': "unknown", "version": 'unknown'},
        }
        
    if user_agent not in cache:
        iam = httpagentparser.detect(user_agent)
        cache[user_agent] = iam if len(iam) else default
        if "dist" not in iam:
            iam['dist'] = default["dist"]
    
    return cache[user_agent]
    



def parse(filename):
    """Return tuple of dictionaries containing file data."""
    log_re= '''^(?P<ip>\S+?)\s# ip
        -\s# dunno
        (?P<user>\S+?)\s# if authentified
        \[(?P<time>.*?)\]\s#apache format
        "(?P<method>.*?)\  #GET/POST/....
        (?P<uri>.*?)\ #add query it would be nice
        HTTP/1.\d"\ # whole scheme (catching FTP ... would be nicer)
        (?P<status>\d+)\ #404 ...
        (?P<bytes>\d+)\ #bytes really bite me if you can
        "(?P<referer>.*?)"\ #where people come from
        "(?P<agent>.*?)"$#well ugly chain'''
    search = re.compile(log_re, re.X).search
    with open(filename) as f:
        for line in f:
            match = search(line)
            if match:
                res = match.groupdict()
                res["fdate"] = dt.strptime(
                     res["time"][:-6],
                    "%d/%b/%Y:%H:%M:%S"
                ).isoformat()
                res["date"] = res["fdate"][:11]
                res["time"] = res["fdate"][11:]
                res["agent_class"] = mnemoize_detect(res["agent"])
                yield res

from json import dumps
from sys import argv


reduce(
    krut.__add__,
    map(
        lambda x : krut(int, {
            "by_country": krut(int, {country(x['ip']): 1}),
            "by_date": krut(int, {x["date"]: 1 }),
            "by_hour": krut(int, {x["time"][0:2]: 1 }),
            "by_os": krut(int, {x["agent_class"]['os']['name']: 1 }),
            "by_dist": krut(int, {x["agent_class"]['dist']['name']: 1 }),
            "by_browser": krut(int, {x["agent_class"]['browser']['name']: 1 }),
            'by_ip': krut(int, {x['ip']: 1 }),
            'by_status': krut(int, {x['status']: 1 }),
            'by_url': krut(int, {x['uri']: 1}),
            'by_agent': krut(int, {x['agent']: 1}),
            'ip_by_url': krut(int, {x['uri']: krut (int, {x['ip']: 1 })}),
            "bytes_by_ip": krut(int, {x['ip']: int(x["bytes"])})
            }
            ),
        filter(
            lambda x: not x['ip'].startswith('192.168'),
            parse(argv[1])
        )
    )
).tprint()
