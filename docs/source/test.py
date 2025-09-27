#!/usr/bin/env python
from archery import mdict
from yahi import notch, shoot
from json import dump
import re


context=notch("/home/jul/trollometre.csv",
    off="user_agent,geo_ip",
    log_format="custom",
    output_format="json",
    date_pattern="%s",
    log_pattern="""^(?P<datetime>[^,]+),
    (?P<nb_fr>[^,]+),
    (?P<nb_total>[^,]+),?.*
    $""")

date_formater= lambda dt :"%s-%s-%s" % ( dt.year, dt.month, dt.day)

res= shoot(
        context,
        lambda data: mdict({
            "date_fr" :
                mdict({ date_formater(data["_datetime"]) : 
                    int(data["nb_fr"]) }),
            "hour_fr" : 
                mdict({ "%02d" % data["_datetime"].hour : 
                    int(data["nb_fr"]) }),
            "date_all" : 
                mdict({ date_formater(data["_datetime"]) : 
                    int(data["nb_total"]) }),
            "hour_all" : 
                mdict({ "%02d" % data["_datetime"].hour : 
                    int(data["nb_total"]) }),
            "total" : 1
        })
    )
dump(res,open("data.js","w"),  indent=4)
