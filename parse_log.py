#!/usr/bin/env python
import re
from vector_dict.VectorDict import VectorDict as krut, convert_tree as kruter
from pygeoip import GeoIP
gi=GeoIP("data/GeoIP.dat")

country = gi.country_code_by_addr

def parse(filename):
    'Return tuple of dictionaries containing file data.'
    def make_entry(x):
        return {
            'ip':x.group('ip'),
            'user' : x.group('user'),
            'uri':x.group('uri'),
            "bytes":x.group("bytes"),
            'time':x.group('time'),
            'status_code':x.group('status_code'),
            'referer':x.group('referer'),
            'agent':x.group('agent'),
            }
  #  log_re = r'(?P<ip>.*?) -(?P<user>.*?)- \[(?P<time>.*?)\] "(?P<method>.*?) (?P<uri>.*?) HTTP/1.\d" (?P<status_code>\d*) (?P<bytes>.*?) "(?P<referral>.*?)" "(?P<agent>.*?)"'
    log_re= '^(?P<ip>.*?) - (?P<user>\S+) \[(?P<time>.*?)\] "(?P<method>.*?) (?P<uri>.*?) HTTP/1.\d" (?P<status_code>\d+) (?P<bytes>\d+) "(?P<referer>.*?)" "(?P<agent>.*?)'
    search = re.compile(log_re).search
    matches = (search(line) for line in open(filename))
#    print [ x and  x.group('ip') or x  for x in matches  ]
    return [make_entry(x)  for x in matches if x  ]

from json import dumps
from sys import argv


reduce( 
    krut.__add__,
    map( 
        lambda x : krut( int, { 
            "country" : krut( int, { country(x['ip']) : 1}),
            'byip"' : krut(int, { x['ip'] : 1 }),
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
