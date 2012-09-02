
- source: https://github.com/jul/yahi
- doc: http://yahi.readthedocs.org/
- ticketting: https://github.com/jul/yahi/issues


Versatile log parser (providing default extractors for apache/lighttpd)
=======================================================================

Command line usage
------------------

Example of data parsed with yahi: http://wwwstat.julbox.fr/

Simplest usage is::
    
    speed_shoot -g /usr/local/data/geoIP /var/www/apache/access*log


it will return a json in the form::
    
    {
        "by_date": {
            "2012-5-3": 11
        }, 
        "total_line": 11, 
        "ip_by_url": {
            "/favicon.ico": {
                "192.168.0.254": 2, 
                "192.168.0.35": 2
            }, 
            "/": {
                "74.125.18.162": 1, 
                "192.168.0.254": 1, 
                "192.168.0.35": 5
            }
        }, 
        "by_status": {
            "200": 7, 
            "404": 4
        }, 
        "by_dist": {
            "unknown": 11
        }, 
        "bytes_by_ip": {
            "74.125.18.162": 151, 
            "192.168.0.254": 489, 
            "192.168.0.35": 1093
        }, 
        "by_url": {
            "/favicon.ico": 4, 
            "/": 7
        }, 
        "by_os": {
            "unknown": 11
        }, 
        "week_browser": {
            "3": {
                "unknown": 11
            }
        }, 
        "by_referer": {
            "-": 11
        }, 
        "by_browser": {
            "unknown": 11
        }, 
        "by_ip": {
            "74.125.18.162": 1, 
            "192.168.0.254": 3, 
            "192.168.0.35": 7
        }, 
        "by_agent": {
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0,gzip(gfe) (via translate.google.com)": 1, 
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0": 10
        }, 
        "by_hour": {
            "9": 3, 
            "10": 4, 
            "11": 1, 
            "12": 3
        }, 
        "by_country": {
            "": 10, 
            "US": 1
        }
    }


If you use::

    speed_shoot -f csv -g /usr/local/data/geoIP /var/www/apache/access*log
    

Your result is::

    by_date,2012-5-3,11
    total_line,11
    ip_by_url,/favicon.ico,192.168.0.254,2
    ip_by_url,/favicon.ico,192.168.0.35,2
    ip_by_url,/,74.125.18.162,1
    ip_by_url,/,192.168.0.254,1
    ip_by_url,/,192.168.0.35,5
    by_status,200,7
    by_status,404,4
    by_dist,unknown,11
    bytes_by_ip,74.125.18.162,151
    bytes_by_ip,192.168.0.254,489
    bytes_by_ip,192.168.0.35,1093
    by_url,/favicon.ico,4
    by_url,/,7
    by_os,unknown,11
    week_browser,3,unknown,11
    by_referer,-,11
    by_browser,unknown,11
    by_ip,74.125.18.162,1
    by_ip,192.168.0.254,3
    by_ip,192.168.0.35,7
    by_agent,"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0,gzip(gfe) (via translate.google.com)",1
    by_agent,Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0,10
    by_hour,9,3
    by_hour,10,4
    by_hour,11,1
    by_hour,12,3
    by_country,,10
    by_country,US,1


Well I guess, it does not work because you first need to fetch geoIP data file::

    wget -O- "http://www.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz" | zcat > /usr/local/data/GeoIP.dat

Of course, this is the geoLite database, I don't include the data in the package
since geoIP must be updated often to stay accurate. 

Default path for geoIP is data/GeoIP.dat

Use as a script
---------------

speed shoot is in fact a template of how to use yahi as a module::

    #!/usr/bin/env python
    from archery.bow import Hankyu as _dict
    from yahi import notch, shoot
    from datetime import datetime


    context=notch()
    date_formater= lambda dt :"%s-%s-%s" % ( dt.year, dt.month, dt.day)
    context.output(
        shoot(
            context,
            lambda data : _dict({
                'by_country': _dict({data['_country']: 1}),
                'by_date': _dict({date_formater(data['_datetime']): 1 }),
                'by_hour': _dict({data['_datetime'].hour: 1 }),
                'by_os': _dict({data['_os_name']: 1 }),
                'by_dist': _dict({data['_dist_name']: 1 }),
                'by_browser': _dict({data['_browser_name']: 1 }),
                'by_ip': _dict({data['ip']: 1 }),
                'by_status': _dict({data['status']: 1 }),
                'by_url': _dict({data['uri']: 1}),
                'by_agent': _dict({data['agent']: 1}),
                'by_referer': _dict({data['referer']: 1}),
                'ip_by_url': _dict({data['uri']: _dict( {data['ip']: 1 })}),
                'bytes_by_ip': _dict({data['ip']: int(data['bytes'])}),
                'week_browser' : _dict({data['_datetime'].weekday():
                    _dict({data["_browser_name"] :1 })}),
                'total_line' : 1,
            }),
        ),
    )



Installation
============

easy as::
    
    pip install yahi

or::
    
    easy_install yahi

Recommanded usage
=================

- for basic log aggregation, I do recommand using command line;
- for one shot metrics I recommend an interactive console (bpython or ipython);
- for specific metrics or elaborate filters I recommand using the API. 


