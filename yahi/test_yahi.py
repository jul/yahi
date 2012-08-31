#/usr/bin/env python
import os
import sys

import unittest
from yahi import shoot, notch
from archery.bow import Hankyu as dict

class FuncTest(unittest.TestCase):
    def setUp(self):
        self.context=notch("",silent=False)

    def test_default(self):
        del(self.context.__dict__["help"])
        del(self.context.__dict__["output"])
        del(self.context.__dict__["files"])
        del(self.context.__dict__["output_file"])
        self.assertEqual(
            self.context.__dict__,
           {'diagnose': '',
             'date_pattern': '%d/%b/%Y:%H:%M:%S',
             'off': (),
             'silent': 'False',
             'log_pattern': None,
             'geoip': 'data/GeoIP.dat',
             'output_format': 'indented_json',
             'data_filter': None,
             'log_pattern_name': 'custom',
             'cache_size': '10000',
             'exclude': None,
             'log_format': 'apache_log_combined',
             'include': None,
             'config': None,
             'skill': ['geo_ip', 'user_agent'],
            }
        )

    def test_parse(self):
        context=notch(
            'yahi/test/biggersample.log', 
            'yahi/test/biggersample.log',
            include="yahi/test/include.json",
            silent=True, 
            exclude='{ "_country" : "US"}', 
            output_format="csv"
        )
        context.diagnose=[ "rejected", "match" ]
        context.data_filter=lambda data: data["_datetime"].hour in [9,10]
        self.assertEqual(
            shoot(context, lambda x: { 
                'total' : 1, 
                "rfc1918":x["ip"].startswith("192.168"),
                "from_gb" : "GB" == x["_country"],
                "hour%d" %  x["_datetime"].hour : 0,

                }),
                {'rfc1918': 844, 'hour9': 0, 'total': 864, 'from_gb': 4, 'hour10': 0},
        )
        self.assertEqual(len(context.log["warning"]),2136)
        context.output({"a":{"b" :1 }})

    def test_loadconfig(self):
        context=notch('',config='yahi/test/config.json')
        context.output(dict(a=1))
        self.assertEqual(
            shoot(context, lambda x: { 
                'total' : 1, 
                "rfc1918":x["ip"].startswith("192.168"),
                "from_gb" : "GB" == x["_country"],
                "hour%d" %  x["_datetime"].hour : 0,

                }),
                {'rfc1918': 0, 'hour9': 0, 'total': 10, 'from_gb': 2}
        )
        self.assertEqual(context.log, { "error": [], "warning" : [] })

