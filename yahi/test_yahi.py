#/usr/bin/env python
import os
from os.path import join
import sys

import unittest
from yahi import shoot, notch
from archery.bow import Hankyu as dict

class FuncTest(unittest.TestCase):
    def setUp(self):
        self.context=notch("",silent=False)
        self.here = os.path.dirname(os.path.realpath(__file__))

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
            join(self.here, 'test/biggersample.log'), 
            join(self.here, 'test/biggersample.log'),
            include=join(self.here,"test/include.json"),
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

    def test_loadconfig(self):
        context=notch('',config=join(self.here,'test/config.json'))
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

    def test_varnish_log(self):
        context=notch('', config=join(self.here,'test/config.varnish.json'))
        res= shoot(context, lambda x: {
            "total" : 1,
            "rfc1918" : x["ip"].startswith('10.'),
            'status_by_uri' : {
                x["uri"].split("?")[1] : { x["cache_status"] :1 
                }
            }, 
            "hour%d" % x["_datetime"].hour: 1}
        )

        self.assertEqual(res,
            {
                'total': 1, 
                'rfc1918': True, 
                'status_by_uri': {
                    'direction=forward': {
                        'miss': 1
                }}, 
                'hour6': 1
            }
        )
        

