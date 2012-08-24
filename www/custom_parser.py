#!/usr/bin/env python
from archery.bow import Hankyu
from yahi.skill import notch, shoot
from time import mktime,strptime
from json import dumps

######################## Setting UP ##################################

option = notch()


##### OKAY, now we can do the job ##########################################

option.output_file.write(
    "data=" + dumps(
        shoot(
            option,
            lambda data : Hankyu({
                'by_country': Hankyu({data['country']: 1}),
                'by_date': Hankyu({data['date']: 1 }),
                'by_hour': Hankyu({"%2d" % int(data['hour']): 1 }),
                'by_os': Hankyu({data['ua_os_name']: 1 }),
                "by_date_as_ts": Hankyu({mktime(
                                strptime(data["date"],'%Y-%m-%d')): 1 }),
                'by_dist': Hankyu({data['ua_dist_name']: 1 }),
                'by_browser': Hankyu({data['ua_browser_name']: 1 }),
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

