====================
Versatile log parser
====================

- source: https://github.com/jul/yahi
- doc: http://yahi.readthedocs.org/
- ticketting: https://github.com/jul/yahi/issues


Synopsis
========

Given a regexp for a log, enables to quicly create
aggregation statisctics by writing few code and generates a all in one web page with all vizualisations and data (that requires javascript to work and has some dependencies).


The library comes with a script that aggregates various data from common log format (apache, nginx) :
*speed_shoot*.

And a script to generate the all in one view *yahi_all_in_one_maker*.

The `demo being there <https://jul.github.io/cv/demo.html?route=chrono#hour_hit>`_

Installation
============
::

    python -m pip install yahi


Quickstart
==========

First you need a geoIP database in legacy format::

    mkdir ~/.yahi
    wget -O- https://mailfud.org/geoip-legacy/GeoIP.dat.gz | \
        zcat > ~/.yahi/GeoIP.dat
    wget -O- https://mailfud.org/geoip-legacy/GeoIPv6.dat.gz | \
        zcat > ~/.yahi/GeoIPv6.dat


And thanks to `mailfud <http://mailfud.org>`_ for keeping these legacy databases.


Simplest usage is::

    speed_shoot /var/log/apache/access*log* > data.js

It reads gzipped file format automatically.

And then::

    yahi_all_in_one_maker data.js

To create a *all in one* HTML page with all JS/CSS/data included that has a multi route view.
It includes various external libraries to work : D3js (charts), jquery.


Use as a script
===============

speed shoot is in fact a template of how to use yahi as a module::

    #!/usr/bin/env python
    from archery import mdict
    from yahi import notch, shoot
    from datetime import datetime


    context=notch()

    date_formater= lambda dt :"%s-%s-%s" % ( dt.year, dt.month, dt.day)
    context.output(
        shoot(
            context,
            lambda data : mdict({
                'by_country': mdict({data['_country']: 1}),
                'date_hit': mdict({date_formater(data['_datetime']): 1 }),
                'date_bandwidth': mdict({date_formater(data['_datetime']): int(data["bytes"]) }),
                'hour_hit': mdict({data['_datetime'].hour: 1 }),
                'hour_bandwidth': mdict({data['_datetime'].hour: int(data["bytes"]) }),
                'by_os': mdict({data['_platform_name']: 1 }),
                'by_dist': mdict({data['_dist_name']: 1 }),
                'by_browser': mdict({data['_browser_name']: 1 }),
                'by_bandwidth_by_browser': mdict({data['_browser_name']: int(data["bytes"]) }),
                'by_ip': mdict({data['ip']: 1 }),
                'by_bandwidth_by_ip': mdict({data['ip']: int(data["bytes"]) }),
                'by_status': mdict({data['status']: 1 }),
                'by_url': mdict({data['uri']: 1}),
                'by_agent': mdict({data['agent']: 1}),
                'by_referer': mdict({data['referer']: 1}),
                'ip_by_url': mdict({data['uri']: mdict( {data['ip']: 1 })}),
                'bytes_by_ip': mdict({data['ip']: int(data['bytes'])}),
                'date_dayofweek_hit' : mdict({data['_datetime'].weekday(): 1 }),
                'weekday_browser' : mdict({data['_datetime'].weekday():
                    mdict({data["_browser_name"] :1 })}),
                'total_line' : 1,
            }),
        ),
    )

Changelog
=========

See `there for changelog <https://github.com/jul/yahi/blob/master/README.md>`_

