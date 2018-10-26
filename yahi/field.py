#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
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
    varnish=re.compile(r'''
(?P<domain>[^ ]+)\s
(?P<ip>\S+?)\s            # ip
-\s                           # dunno
-\s                           # dunno
\[(?P<datetime>[^\]]+)\s      # apache format
(?P<tz_offset>[+-]\d{4})\]\s  #
"(?P<method>[A-Z]+)\s          # GET/POST/....
(?P<uri>[^ ]+)\s               # add query it would be nice
(?P<scheme>[A-Z]+(\/1)?).?\d?"\                   # whole scheme (catching FTP ... would be nicer)
(?P<status>\d+)\              # 404 ...
(?P<bytes>\d+)\               # bytes really bite me if you can
"(?P<referer>[^"]+)"\         # where people come from
"(?P<agent>[^"]+)"\ 
"(?P<cache_status>[^"]+)"\ 
"(?P<protocol>[^"]+)"$           # well ugly chain''', re.VERBOSE),
)

date_pattern = dict( 
    apache_log_combined = "%d/%b/%Y:%H:%M:%S",
    varnish = "%d/%b/%Y:%H:%M:%S",
    lighttpd = "%d/%b/%Y:%H:%M:%S",
)
