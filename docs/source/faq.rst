===
FAQ
===

Fusinoning two data files (in JSON)
***********************************


::

    from archery.barrack import bowyer
    from archery import mdict
    from json import load, dumps
    dumps(
            bowyer(mdict,load(file("dat1.json"))) +
            bowyer(mdict,load(file("dat2.json")))
        )


