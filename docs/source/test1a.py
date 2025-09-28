from yahi.field import regexp_reader
from archery import mdict
from datetime import datetime as dt
import re
from json import dumps

hr = lambda ts: "%02d" % dt.fromtimestamp(float(ts)).hour
date = lambda ts: dt.fromtimestamp(float(ts)).strftime("%y-%m-%d")

print(dumps(
    sum(
        mdict(
            date_fr=mdict({
                date(r["datetime"]) : int(r["nb_fr"]) }),
            hour_fr=mdict({
                hr(r["datetime"]) : int(r["nb_fr"]) }),
        ) for r in regexp_reader(
            open("/home/jul/trollometre.csv"), 
            re.compile("""^(?P<datetime>[^,]+),
                (?P<nb_fr>[^,]+),
                (?P<nb_total>[^,]+),?.*
                $""", 
                re.X
            )
        )
    ),
    indent=4)
)
