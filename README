
- source: https://github.com/jul/yahi
- doc: http://yahi.readthedocs.org/
- ticketting: https://github.com/jul/yahi/issues


Versatile log parser (providing default extractors for apache/lighttpd)
=======================================================================

Command line usage
------------------

Example of data parsed with yahi: http://wwstat.julbox.fr/

Simplest usage is::
    
    speed_shoot -g /usr/local/data/geoIP /var/www/apache/access*log

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


    ######################## Setting UP ##################################
    # parsing command line & default settings. Return a context
    context=notch()
    ##### OKAY, now we can do the job #################################### 
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

Recommanded usage
=================

- for basic log aggregation, I do recommand using command line;
- for one shot metrics I recommend an interactive console (bpython or ipython);
- for specific metrics or elaborate filters I recommand using the API. 


