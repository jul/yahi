# Versatile log parser

- source: https://github.com/jul/yahi
- doc: http://yahi.readthedocs.org/
- ticketting: https://github.com/jul/yahi/issues


# Synopsis

Given a regexp for a log, enables to quicly create
aggregation statisctics by writing few code and generates a all in one web page with all vizualisations and data (that requires javascript to work and has some dependencies).


The library comes with a script that aggregates various data from common log format (apache, nginx) :
*speed_shoot*.

And a script to generate the all in one view *yahi_all_in_one_maker*.

The [demo being there](https://jul.github.io/cv/demo.html?route=chrono#hour_hit)

# Installation


```
    pip install yahi
```

# Quickstart

First you need a geoIP database in legacy format::
```
    mkdir data
    wget -O- https://mailfud.org/geoip-legacy/GeoIP.dat.gz | zcat > data/GeoIP.dat
```
And thanks to `mailfud <http://mailfud.org>`_ for keeping these legacy databases.


Simplest usage is:
```
    speed_shoot -g /usr/local/data/geoIP.dat /var/www/apache/access*log* > data.js
```

It reads gzipped file format automatically.

And then:
```
    yahi_all_in_one_maker data.js
```

To create a *all in one* HTML page with all JS/CSS/data included that has a multi route view.
It includes various external libraries to work : D3js (charting), jquery, google js api (geo chart).

# Screenshots

## Time serie
<image src="https://raw.githubusercontent.com/jul/yahi/refs/heads/master/docs/source/img/chrono.png">

## Histograms

<image src="https://raw.githubusercontent.com/jul/yahi/refs/heads/master/docs/source/img/histo.png">

## Geographic map

<image src="https://raw.githubusercontent.com/jul/yahi/refs/heads/master/docs/source/img/geo.png">

## Raw data

<image src="https://raw.githubusercontent.com/jul/yahi/refs/heads/master/docs/source/img/raw.png">



# Use as a script

speed shoot is in fact a template of how to use yahi as a module::

```python
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
```

# Naming

Archery is a pun on trait.

[Yahi](https://en.wikipedia.org/wiki/Ishi) is a remembrance of a native american tribes that was versed in
archery so that somewhere on the net we remember the genocides committed in the
name of civilisation.

Yahi is thus a concrete application of archery for aggregation based on 2
functions : 

- notch to prepare your log aggregations
- shoot to actually aggregate


Let's have a thought for the native americans that are still second ranks
citizens in their own lands. 





# Changelog

## 0.1.19-0.1.20

* wording in README

## 0.1.8

* adding tests in the package so package does not install if tests dont pass

## 0.1.7

* oopsies removed needless pictures of the package

## 0.1.6

* adding yahii\_all\_in\_one\_maker to generate the all in one HTML file with
visualization from speed\_shoot

## 0.1.5

* preparing a new release that generates all in one html static pages

## 0.1.3

Adding varnish incomplete regexp for log parsing (I miss 2 fields)

## 0.1.1

* bad url for the demo  

## 0.1.0

* it is NEW, seen on TV, and is guaranteed to make you tenfolds more desirable. 



