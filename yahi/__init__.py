#i!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from warnings import warn
from os import path
import re
from datetime import datetime
try:
    import pygeoip
except ModuleNotFoundError:
    warn("pygeoip required for full feartures" ,ImportWarning)
try:
    import httpagentparser
except ModuleNotFoundError:
    warn("httpagentparser required for full features", ImportWarning)

import fileinput
import csv
from json import load, loads, dump, dumps
from archery.trait import Copier
from archery.barrack import mapping_row_iter
from archery.bow import Hankyu 
from .field import log_pattern, date_pattern
from repoze.lru import lru_cache
import argparse
import locale
locale.setlocale(locale.LC_ALL,"C")



class ToxicSet(Copier,set):
    """a set for wich add is a shortcut for union
    this way, I can now select all the distinct stuffs
    However, I am pretty convinced I'd rather not see that too much. 
    I have a legitimate use for it, but I do have the feeling to
    solve a problem in a PHPish solution
    Some people want to watch the world burn. 
    """
    def __iadd__(x,y):
        x|=y
        return x

    def __add__(x,y):
        return x|y
    def to_json(self):
        return list(self) 
    def __str__(self):
        return str(list(self))
    def __repr__(self):
        return repr(list(self))

####################### STATIC DATA ################################
HARDCODED_GEOIP_FILE = "data/GeoIP.dat"
### GLOBAL CACHE prettu multiprocessing unfirendly


####################" 


def build_filter_from_json(str_or_file, positive_logic):
    matcher = {}
    if type(str_or_file) is dict:
        matcher=str_or_file
    else:
        try:
            matcher=loads(str_or_file)
        except ValueError:
            with open(str_or_file) as f:
                matcher = load(f)

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
    if not len(matcher):
        raise Exception("Lapin compris")
   
####################### UTILITIES ################################
def dt_formater_from_format(date_format):
    def cdt_format(dt):
        return datetime.strptime(dt,date_format)
    return cdt_format


def normalize_user_agent(user_agent):
    """
    set default value for useragent and
    flatten httpuseragentparser result, in the form ua_%(key)s_%(subkey)s
    key in ["os", "browser", "dist" ]
    subkey in ["name", "version" ]
    """
    flat=dict()
    user_agent = {
        'os': {'name': "unknown", "version": 'unknown'},
        'browser': {'name': "unknown", "version": 'unknown'},
        'dist': {'name': "unknown", "version": 'unknown'},
        }
    user_agent.update( httpagentparser.detect(user_agent))
    flat=dict()
    for k in user_agent:
        for sub_key,v in user_agent[k].items():
            flat.update({ "_" + "_".join([ k, sub_key]) :v}) 
    return flat
    
def shoot( context, group_by,):
    """Produce a dict of the data found in the line.
    and use group_by to  group according to option (that can contain 
    a data_filter)
    * group_by : a lambda returning a Hankyu (dict)
        used to extract the valid informations
    * option.cache : cache strategy (beaker, repoze, dict, fixed, no_cache)
    * option.data_filter : f(data) => bool
        applies to the data dict, 
        if True extract the current data
    * option.diagnose array of string : 
      * match : tells on stderr wich line were rejected
      * rejected : tells stderr wich data were filtered out
    * option.skill : enable costly extraction of : 
        * geo_ip : geoip informations
        * user_agent : user_agent parsing
    * option.log_format : apache_log_combined or lighttpd
        tells the regexp to use to extract the fields from the line
        also used to select the datetime parser
    """
    context.log=dict(error=[],warning=[]) 
    aggregator=Hankyu({})
    if 'user_agent' in context.skill:
        import httpagentparser
    
    look_for = log_pattern[context.log_format].search
    match = None
    dt_format = dt_formater_from_format(date_pattern[context.log_format])
    parse_user_agent = lru_cache(context.cache_size)(normalize_user_agent)
    if "geo_ip" in context.skill:
        from pygeoip import GeoIP
        gi = GeoIP(context.geoip)
        country_by_ip = lru_cache(context.cache_size)(gi.country_code_by_addr)
    _input = fileinput.input(context.files)
    if not context.silent:
        sys.stderr.write("parsing:\n %s\n" % "\n-" . join(context.files))
    try:
        for line in _input:
            match = look_for(line)
            if not context.silent and not _input.lineno() % 10000:
                sys.stderr.write("*")
                
            if match:
                data = match.groupdict()
                if data.get("datetime"):
                    data['_datetime']=dt_format(data["datetime"])

                if 'geo_ip' in context.skill:
                    data.update( {"_country":country_by_ip(data["ip"])})
                if 'user_agent' in context.skill:
                    data.update(
                        parse_user_agent(data["agent"])
                    )
                if context.data_filter and not context.data_filter(data):
                    if "rejected" in context.diagnose:
                        if context.silent:
                            context.log["warning"]+=[ "REJECTED:at %s:%s:%s"%(
                                _input.lineno(),_input.filename(),data) ]
                        else:
                            sys.stderr.write("at %s:%s:" % (
                                _input.lineno(),_input.filename()) )
                            sys.stderr.write("REJECTED:{0}\n".format(data))
                else:
                    aggregator += group_by(data)
            elif "match" in context.diagnose:
                if context.silent:
                    context.log["warning"]+=[
                        "NOTMATCH:at %s:%s:\%s not match" % ( 
                        _input.lineno(),_input.filename(), line)]
                else:
                    sys.stderr.write("at %s:%s:" % ( 
                        _input.lineno(),_input.filename()) )
                    sys.stderr.write("NOT MATCHED:«{0}»\n".format(line))
    except Exception as e:
        if context.silent is True:
            context.log["error"]+=["ARRG(%s):at %s:%s" % (e, _input.lineno(),_input.filename())]
        else:
            sys.stderr.write("ARRG:at %s:%s\n" % ( 
                _input.lineno(),_input.filename()) )
            sys.stderr.write("CONTEXT:match %s:data : %s\n" % (
                match and match.groupdict() or "no_match",data))
            raise Exception(e)
    finally:
        ## causes a problem with stdin/stderr
        #_input.close()
        if not context.silent:
            sys.stderr.write("\n%s lines parsed\n" % _input.lineno())
    return aggregator

#################### CLI and DOC #################################

def notch(*_file,**option):
    """CLI parser
    returns an context object that contains all CLI params and values
    print( notch().help ) for more informations
    
    Default values are the same as with the CLI, available options are:
        - exclude,
        - include,
        - output_format,
        - output_file,
        - log_pattern,
        - date_pattern,
        - off (turning off user_agent detection or geoIP),
        - log_pattern_name,
        - cache_size,
"""

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
    parser.add_argument("-q",
        "--silent",
        help="quietly discard errors",
        default=False
    )
    parser.add_argument("-cs",
        "--cache-size",
        help="in conjonction with cp=fixed chooses dict size",
        default="10000"
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

    parser.add_argument("-i",
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
        help="""decide if output is in a specified formater amongst : csv, json
        """,
        default="indented_json"
    )
    parser.add_argument("-lf",
        "--log-format",
        help="log format amongst apache_log_combined, lighttpd",
        default="apache_log_combined"
    )
    parser.add_argument("-lp",
        "--log-pattern",
        help="""add a custom named regexp for parsing log lines""",
    )
    parser.add_argument("-lpn","--log-pattern-name",
        help="""the name with witch you want to register the pattern""",
        default="custom"
    )

    parser.add_argument("-dp",
        "--date-pattern",
        help="""add a custom date format, usefull if and only if using 
        a custom log_pattern and date pattern differs from apache.""",
        default=date_pattern["apache_log_combined"]
    )

    parser.add_argument("-o",
        "--output-file",
        help="output file",
        type=argparse.FileType('w'),
        default=sys.stdout
    )
    parser.add_argument('files', nargs=argparse.REMAINDER)
    if option or _file:
        arg=[]
        for k, v in option.items():
            arg+=[ ("--%s" %k).replace("_","-") ]
            arg+=["%s" % v] 
        if _file : arg+=  _file 
        if __file__ in sys.argv:
            _from = index(__file__)
            arg+=[sys.argv[_from+1:]]
        context=parser.parse_args(arg )
    else:
        context=parser.parse_args()

    context.skill=[]

    # loading if needed options as a json
    if context.config:
        with open(context.config) as config_json:
            config_args = loads(config_json.read())
        for k in config_args:
            setattr(context, k, config_args[k])
            if "output_file" == k:
                context.output_file=open(config_args[k],"w")
    # sanity check
    if context.log_pattern and context.log_format != context.log_pattern_name:
        raise Exception("You want to register a new pattern and not use it?")

    # hu hu I wouldn't like to see a log pattern on the command line
    # advice: use the json to load load log format, or send a patch
    # it will be easier. 
    if context.log_pattern:
        log_pattern[context.log_pattern_name]=re.compile(
            context.log_pattern,
            re.VERBOSE
        )

        if context.date_pattern:
            date_pattern[context.log_pattern_name]=context.date_pattern

    # crude filtering with regexps matching a regexp for given keys
    if not option.get('data_filter'):
        _data_filter = None
        _exclusive_filter = _inclusive_filter = None
        if context.include:
            _data_filter= _inclusive_filter = build_filter_from_json(
                context.include,True
            )

        if context.exclude:
            _data_filter = _exclusive_filter = build_filter_from_json(
                context.exclude,False
            )

        if _exclusive_filter and _inclusive_filter:
            _data_filter = lambda data : _exclusive_filter(data) and \
                _inclusive_filter(data)

        context.data_filter=_data_filter

    def csv_formater(aggreg,**kw):
        csv.writer(context.output_file).writerows(mapping_row_iter(aggreg))
        ### py3/bpython nawak
        try:
            #I close file or .... I create bug when input is stdout/stderr
            #context.output_file.close()
            pass
        except:
            pass

    def json_formater(aggreg, **kw):
        output=context.output_file
        dump(aggreg, output,**kw)

    context.output=dict( 
        csv = csv_formater,
        json = json_formater,
        indented_json = lambda a,**kw: json_formater(a,indent=4,**kw)
    )[context.output_format]

    if "geo_ip" not in context.off:
        context.skill+= [ "geo_ip" ]

    if "user_agent" not in context.off:
        context.skill+= [ "user_agent" ]

    context.help = parser.format_help()
    for k,v in context.__dict__.items():
        setattr(context,k,v)

    return context

