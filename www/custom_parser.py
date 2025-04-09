#!/usr/bin/env python
from archery.bow import Hankyu
from yahi import notch, shoot
from time import mktime,strptime, time
from json import dumps
from datetime import datetime as dt
import datetime

######################## Setting UP ##################################

option = notch()


##### OKAY, now we can do the job ##########################################

option.output_file.write(
    "data=" + dumps(
        shoot(
            option,
            lambda data : Hankyu({
                'by_country': Hankyu({data['_country']: 1}),

                'by_date': # Hankyu({str(data['_datetime']): 1 }),
                    Hankyu({str(dt.combine(data["_datetime"],datetime.time(0,0,0)).date()): 1 }),
                'by_hour': Hankyu({"%2d" % int(data['_hour']): 1 }),
                'by_os': Hankyu({data['_os_name']: 1 }),
                "by_date_as_ts": Hankyu({
                    dt.combine(data["_datetime"],datetime.time(0,0,0)).timestamp(): 1 }),
                'by_dist': Hankyu({data['_dist_name']: 1 }),
                'by_browser': Hankyu({data['_browser_name']: 1 }),
                'by_ip': Hankyu({data['ip']: 1 }),
                'by_status': Hankyu({data['status']: 1 }),
                'by_url': Hankyu({data['uri']: 1}),
                'by_agent': Hankyu({data['agent']: 1}),
                'by_referer': Hankyu({data['referer']: 1}),
                'ip_by_url': Hankyu({data['uri']: Hankyu( {data['ip']: 1 })}),
                'bytes_by_ip': Hankyu({data['ip']: int(data['bytes'])}),
                'total_line' : 1,
            }),
        ),
        indent=4
    )
)

