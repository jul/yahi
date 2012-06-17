#!/usr/bin/env python
from archery.bow import Hankyu
from yahi.barrack import option_from_arg_parser, memoize, aggregates

######################## Setting UP ##################################

option = option_from_arg_parser()


##### OKAY, now we can do the job ########################################## 

option.skill=['user_agent', 'geo_ip'] 

option.output(
    option.output_file,
    aggregates(
            lambda data : Hankyu({
            'by_country': Hankyu({data['country']: 1}),
            'by_date': Hankyu({data['date']: 1 }),
            'by_hour': Hankyu({data['hour']: 1 }),
            'by_os': Hankyu({data['ua_os_name']: 1 }),
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
        option,
    )
)

