.. yahi documentation master file, created by
   sphinx-quickstart on Thu Jul 19 13:31:16 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Contents:

.. toctree::
   cli_arg.rst
   logic.rst
   console.rst
   custom_script.rst
   misusing.rst
   


Shooting web log (apache included) like a native american
=========================================================

I like stretching the archery metaphor. Archery is a tool, yahi is an ancient
tribe that was known for its skill with a bow. 

yahi is a useful exemple of it. 

I use it here: http://wwstat.julbox.fr/

Simplest usage is::

    speed_shoot -g /usr/local/data/geoIP /var/www/apache/access*log

Well I guess, it does not work because you first need to fetch geoIP data file::

    wget -O- "http://www.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz" | zcat > /usr/local/data/GeoIP.dat

Default path for geoIP is data/GeoIP.dat

Recommanded usage
=================

- for basic log aggregation, I do recommand using command line;
- for one shot metrics I recommend an interactive console (bpython or ipython);
- for specific metrics or elaborate filters I recommand using the API. 




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

