#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import IO, Pattern, AnyStr, Pattern
import re
log_pattern=dict( 
    apache_log_combined = re.compile(
'''^(?P<ip>[^ ]+)\s           # ip
(?P<userider>[^ ]+)\s         # RFC1413 user identifier
(?P<user>[^ ]+)\s             # if authentified
\[(?P<datetime>[^\]]+)\s      # apache format
(?P<tz_offset>[+-]\d{4})\]\s  #
"(?P<method>[A-Z]+)\ ?         # GET/POST/....
(?P<uri>[^ ]+)\ ?              # add query it would be nice
(?P<scheme>[A-Z]+(\/.)?.\d)"\                   # whole scheme (catching FTP ... would be nicer)
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
    varnish=re.compile(r'''
(?P<domain>[^ ]+)\s
(?P<ip>\S+?)\s            # ip
-\s                           # dunno
-\s                           # dunno
\[(?P<datetime>[^\]]+)\s      # apache format
(?P<tz_offset>[+-]\d{4})\]\s  #
"(?P<method>[A-Z]+)\s          # GET/POST/....
(?P<uri>[^ ]+)\s               # add query it would be nice
(?P<scheme>[A-Z]+(\/.)?.\d)?"\                   # whole scheme (catching FTP ... would be nicer)
(?P<status>\d+)\              # 404 ...
(?P<bytes>\d+)\               # bytes really bite me if you can
"(?P<referer>[^"]+)"\         # where people come from
"(?P<agent>[^"]+)"\ 
"(?P<cache_status>[^"]+)"\ 
"(?P<protocol>[^"]+)"$           # well ugly chain''', re.VERBOSE),
)
log_pattern["nginx"] = log_pattern["apache_log_combined"]


date_pattern = dict( 
    apache_log_combined="%d/%b/%Y:%H:%M:%S",
    varnish="%d/%b/%Y:%H:%M:%S",
    lighttpd="%d/%b/%Y:%H:%M:%S",
)
date_pattern["nginx"] = date_pattern["apache_log_combined"]



def regexp_reader(file : IO, pattern_name_or_regexp : Pattern | str) :
    if pattern_name_or_regexp not in log_pattern and type(pattern_name_or_regexp) != re.Pattern:
        raise Exception("invalid input, expected string or valid log_pattern")
    pattern = log_pattern.get(pattern_name_or_regexp, pattern_name_or_regexp)
    for l in file:
        if match := pattern.match(l):
            yield match.groupdict()
