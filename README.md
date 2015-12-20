statusboard-librato
===================

`statusboard-librato` acts as a bridge between Librato's API and Panic's
Status Board.


Installation
============

Installation works well on Heroku, but will work fine anywhere. All
requirements are specified in `requirements.txt`. It's set up to `gunicorn`
but use your WSGI app of choice (eg, `uWSGI`).

Set `LIBRATO_USER` and `LIBRATO_TOKEN` environment variables to their
respective values.

Usage
=====

To use, make a request to `/metrics/<metric_name>/<source>`,

where <metric_name> is the name of your metric in Librato and <source> is
the source to use.


Limitations
===========

* Only a single metric+source combination are supported
* Output is locked to line graphs only
* No authentication
