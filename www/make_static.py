#!/usr/bin/env python
with open("./data.js") as f:
    DATA=f.read()
    with open("./static.template") as g:
        res = g.read().replace("{{DATA}}", DATA)


        with open("aio.html", "w") as h:
            h.write(res)

