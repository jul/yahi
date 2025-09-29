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

                'heat_by_day' : mdict({ data['_datetime'].strftime("%w:%Y %W") : 1}),
                'heat_by_hour' : mdict({ data['_datetime'].strftime("%H:%Y/%j %m-%d") : 1}),
                'hour_bandwidth': 
                    mdict({
                        "%2d" % int(data['_hour']):
                        int(data["bytes"]) 
                    }),
                'by_os': mdict({data['_platform_name']: 1 }),
                'by_dist': mdict({data['_dist_name']: 1 }),
                'by_browser': mdict({data['_browser_name']: 1 }),
                'by_status': mdict({data['status']: 1 }),
                'by_scheme': mdict({data['scheme']: 1 }),
                'by_bandwidth_by_scheme': mdict({data['scheme']: int(data["bytes"]) }),
                'by_agent': mdict({data['agent'][:40] + "...": 1}),
                'total_line' : 1,
            }),
        ),
        indent=4
    )
)

