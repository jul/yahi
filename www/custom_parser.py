#!/usr/bin/env python
from archery.bow import mdict
from yahi import notch, shoot
from time import mktime,strptime, time
from json import dumps
from datetime import datetime as dt
import datetime

######################## Setting UP ##################################

option = notch()


##### OKAY, now we can do the job ##########################################

option.output_file.write(
    dumps(
        shoot(
            option,
            lambda data : mdict({
                'by_country': mdict({data['_country']: 1}),
                'date_bandwidth': 
                    mdict({
                        str(data["_datetime"].date()): int(data["bytes"])
                    }),
                'date_hit': mdict({str(data['_datetime'].date()): 1 }),
                'hour_hit': mdict({"%2d" % int(data['_hour']): 1 }),
                'hour_bandwidth': 
                    mdict({
                        "%2d" % int(data['_hour']):
                        int(data["bytes"]) 
                    }),
                'by_os': mdict({data['_platform_name']: 1 }),
                'by_dist': mdict({data['_dist_name']: 1 }),
                'by_browser': mdict({data['_browser_name']: 1 }),
                'by_ip': mdict({data['ip']: 1 }),
                'by_status': mdict({data['status']: 1 }),
                'by_url': mdict({data['uri']: 1}),
                'by_agent': mdict({data['agent'][:40] + "...": 1}),
                'by_referer': mdict({data['referer']: 1}),
                'ip_by_url': mdict({data['uri']: mdict( {data['ip']: 1 })}),
                'bytes_by_ip': mdict({data['ip']: int(data['bytes'])}),
                'total_line' : 1,
            }),
        ),
        indent=4
    )
)

