from yahi.field import regexp_reader
from archery import mdict
from urllib.parse import urlparse

res="""digraph {
      rankdir=LR;
      splines=false;
      node [
        shape=record
      ]

"""
for k,v in sum(
        mdict({(r["referer"], r["uri"]):1}) for r in
            regexp_reader(
                open("/var/log/nginx/access.log.1"),
                "nginx"
            )
        ).items():
    if urlparse(k[0]).netloc == 'localhost' and k[0] != '-':
        res+=f"""  "{urlparse(k[0]).path}" -> "{k[1]}" [label="{v} hits" ]\n """

res+="\n}"
print(res)
