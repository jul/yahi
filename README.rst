Versatile log parser (providing default extractors for apache/lighttpd)
=======================================================================

Command line usage
------------------

Example of data parsed with yahi: http://wwstat.julbox.fr/

Simplest usage is::
    speed_shoot -g /usr/local/data/geoIP /var/www/apache/access*log

Well I guess, it does not work because you first need to fetch geoIP data file::

    wget -O- "http://www.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz" | zcat > /usr/local/data/GeoIP.dat

Default path for geoIP is data/GeoIP.dat

Use as a script
---------------

speed shoot is in fact a template of how to use yahi as a facility

.. literalinclude:: ../../speed_shoot

Recommanded usage
=================

- for basic log aggregation, I do recommand using command line;
- for one shot metrics I recommend an interactive console (bpython or ipython);
- for specific metrics or elaborate filters I recommand using the API. 


