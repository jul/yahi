#!/usr/bin/env python
import re
from vector_dict.VectorDict import VectorDict as krut, convert_tree as kruter
from pygeoip import GeoIP
from datetime import datetime as dt 
import time
gi=GeoIP("data/GeoIP.dat")

country = gi.country_code_by_addr

def parse(filename):
    'Return tuple of dictionaries containing file data.'
    log_re= '^(?P<ip>.*?) - (?P<user>\S+) \[(?P<time>.*?)\] "(?P<method>.*?) (?P<uri>.*?) HTTP/1.\d" (?P<status_code>\d+) (?P<bytes>\d+) "(?P<referer>.*?)" "(?P<agent>.*?)'
    search = re.compile(log_re).search
    with open(filename) as f:
        for line in f:
            match = search(line)
            if match:
                res=match.groupdict()
                res["fdate"] = dt.strptime(
                     res["time"][:-6], 
                    "%d/%b/%Y:%H:%M:%S"
                ).isoformat()
                res["date"]=res["fdate"][:11]
                res["time"]=res["fdate"][11:]


                yield res

from json import dumps
from sys import argv


reduce( 
    krut.__add__,
    map( 
        lambda x : krut( int, { 
            "by_country" : krut( int, { country(x['ip']) : 1}),
            "by_date" : krut(int, { x["date"] : 1 }),
            "by_hour" : krut(int, { x["time"][0:2] : 1 }),
            'by_ip' : krut(int, { x['ip'] : 1 }),
            'by_url': krut(int,{x['uri']  : 1}),
            'ip_by_url' : krut( int, {x['uri']  : krut ( int, {x['ip'] : 1 })}),
            "bytes_by_ip"  : krut ( int, {x['ip'] : int(x["bytes"]) })
            }
            ),
        filter( 
            lambda x : not x['ip'].startswith('192.168'),
            parse(argv[1])
        )
    )
).tprint()
