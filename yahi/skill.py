#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os import path
import re
from datetime import datetime
import pygeoip
import httpagentparser
import fileinput
import csv
from json import load, loads, dump, dumps
from functools import wraps
from archery.bow import Hankyu
from archery.barrack import mapping_row_iter
import argparse


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
def build_filter_from_json(str_or_file, positive_logic):
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
        if positive_logic:
            return lambda data : all(
                matcher[k](data[k]) for k in matcher
            ) if data else False
        else:
            return lambda data : not(
                any(matcher[k](data[k]) for k in matcher )
            ) if data else False
 
   
####################### UTILITIES ################################
def memoize(cache):
    """A simple memoization decorator.
Only functions with positional arguments are supported."""
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args):
            if args not in cache:
                cache[args] = fn(*args)
            return cache[args]
        return wrapped
    return decorator

def cached_date_time_formater(date_format):
    _DATE_TIME_FORMATER={}
    def cdt_format(dt):
        if not dt in _DATE_TIME_FORMATER:
            _DATE_TIME_FORMATER.update({ dt: datetime.strptime(dt,date_format)})
        return _DATE_TIME_FORMATER[dt]
    return cdt_format 

def date_formater(date):
    _CACHE_DATE = {}
    if not date in _CACHE_DATE:
        _CACHE_DATE.update( { date : date.strftime('%Y-%m-%d') } )
    return _CACHE_DATE[date]


def flatten_user_agent(user_agent):
    flat=dict()
    for k in user_agent:
        for sub_key,v in user_agent[k].iteritems():
            flat.update({ "_".join(["ua" , k, sub_key]) :v}) 
    return flat

_CACHE_UA = {}
@memoize(_CACHE_UA)
def normalize_user_agent(user_agent):
    default_user_agent = {
        'os': {'name': "unknown", "version": 'unknown'},

        'browser': {'name': "unknown", "version": 'unknown'},
        'dist': {'name': "unknown", "version": 'unknown'},
        }
    default_user_agent.update( httpagentparser.detect(user_agent) )
    return flatten_user_agent(default_user_agent )


def grouped_shooting(
        option,
        group_by,
        ):
    """Produce a dict of the data found in the line.
    If the line is not recognized, return None.
    
    """
    aggregator=Hankyu()
    if 'user_agent' in option.skill:
        import httpagentparser
    look_for = log_pattern[option.log_format].search
    match = None
    date_log_formater= cached_date_time_formater(date_format[option.log_format])

    if "geo_ip" in option.skill:
        _CACHE_GEOIP = {}
        from pygeoip import GeoIP
        gi = GeoIP(option.geoip)
        country_by_ip = memoize(_CACHE_GEOIP)(gi.country_code_by_addr)
    _input = fileinput.input(option.files) 
    try: 
        for line in _input:
            
            match = look_for(line)
            if match:
                data = match.groupdict()
                _datetime=date_log_formater(data["datetime"])
                data.update( dict(
                    date = date_formater(_datetime),
                    hour = str(_datetime.hour)
                ))

                if 'geo_ip' in option.skill:
                    data.update( {"country":country_by_ip(data["ip"])})
                if 'user_agent' in option.skill:
                    data.update(
                        normalize_user_agent(data["agent"])
                    )
                if option.data_filter and not option.data_filter(data):
                    if "rejected" in option.diagnose:
                        sys.stderr.write("REJECTED:{0}\n".format(data))
                else:
                   aggregator+=group_by(data)

            elif "match" in option.diagnose:
                sys.stderr.write("NOT MATCHED:{0}\n".format(line))
    except Exception as e:
        raise Exception(e)
    finally:
        _input.close()
    
    return aggregator

#################### CLI and DOC #################################

def notch(*a,**kw):
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

Example :
=========

from stdin (useful for using zcat)
**********************************
zcat /var/log/apache.log.1.gz | parse_log.py  > dat1.json

excluding IPs 192.168/16 and user agent containing Mozilla
**********************************************************
parse_log -o dat2.json -x '{ "ip" : "^192.168", "agent": "Mozill" }'  /var/log/apache*.log 

Since archery is cool here is a tip for aggregating data
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
        metavar="FILE",
        default=None
        )
    parser.add_argument("-g",
        "--geoip",
        help="specify a path to a geoip.dat file",
        default=HARDCODED_GEOIP_FILE
    )
    parser.add_argument("-d",
        "--diagnose",
        help="""diagnose 
            list of space separated arguments :
                **rejected** : will print on STDERR rejected parsed line,
                **match** : will print on stderr data filtered out
        
        """,
        default="",
        nargs='+',
        
    )
        
    parser.add_argument("-in",
        "--include",
        help="""include from extracted data with
        a json (string or filename) in the form { "field" : "pattern" } """,
    )
    parser.add_argument(
        "--off",
        help="""turn off plugins : geo_ip to skip geoip, user_agent to
        turn httpagentparser off""",
        default=()
    )
    parser.add_argument("-x",
        "--exclude",
        help="""exclude from extracted data with
        a json (string or filename) in the form { "field" : "pattern" } """,
    )
    parser.add_argument("-f",
        "--output-format",
        help="""decide if output is in a specified formater amongst : csv, json,
        indented_json""",
        default="indented_json"
    )
    parser.add_argument("-lf",
        "--log-format",
        help="log format amongst apache_log_combined, lighttpd",
        default="apache_log_combined"
    )

    parser.add_argument("-o",
        "--output-file",
        help="output file",
        type=argparse.FileType('w'),
        default=sys.stdout
    )
    parser.add_argument('files', nargs=argparse.REMAINDER)
    option=parser.parse_args(*a,**kw)
    option.skill=[]

    if option.config:
        config_args = load(open(option.config))
        for k in config_args:
            if not getattr(option,k):
                setattr(option, k, config_args[k])
            if "output_file" == k:
                option.output_file=open(config_args[k],"w")

    _data_filter = None
    _exclusive_filter = _inclusive_filter = None
    if option.include:
        _data_filter= _inclusive_filter = build_filter_from_json(option.include,True)

    if option.exclude:
       _data_filter = _exclusive_filter = build_filter_from_json(option.exclude,False)
    
    if _exclusive_filter and _inclusive_filter:
        _data_filter = lambda data : _exclusive_filter(data) and \
            _inclusive_filter(data)

    option.data_filter=_data_filter
    option.output=dict( 
        csv = lambda aggreg : csv.writer(option.output_file).writerows( 
            mapping_row_iter(aggreg)
        ),
        json = lambda aggreg : option.output_file.write( dumps(aggreg)),
        indented_json = lambda aggreg : option.output_file.write(
            dumps(aggreg,indent=4
         )),
    )[option.output_format]
    if "geo_ip" not in option.off:
        option.skill+= [ "geo_ip" ]
    if "user_agent" not in option.off:
        option.skill+= [ "user_agent" ]
    option.help = parser.format_help()
    return option
    
