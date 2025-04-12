==================
For the intreprids
==================


Requirements:
-------------


A valid legacy geoIP.dat in data/geoIP.dat that can be found on
`mailfud <https://mailfud.org/geoip-legacy/>`. It is treated later.


doing
-----

The parsing is done with this command::

    python custom_parser.py ../*log* > data.js

then do::

    python make_static.py && firefox aio.html

and enjoy the result : as you have a single app web page (require javascript
activated, sorry w3m users)

A `full functional example is there <demo.html>`

Screenshots
-----------

* *Geo IP rendering*

.. image:: img/geo.png

* *Top n charts*

.. image:: img/histo.png

* *Date rendering*

.. image:: img/chrono.png

* *Raw data*

.. image:: img/raw.png
