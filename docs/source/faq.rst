===
FAQ
===

I want to use speed_shoot to parse a format unknown to it like LDAP logs
************************************************************************

If it is a ponctual case there is an `example here <https://github.com/jul/yahi/blob/master/examples/parse_etc>`_ 
which includes both a custom regexp and a custom logic for aggregation.

If it is a more common case, I accept contribution with *anonymised* logs for testing.

The `regexp are defined here <https://github.com/jul/yahi/blob/master/yahi/field.py>`_ and should be :

- named regexp;
- commentend.



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


