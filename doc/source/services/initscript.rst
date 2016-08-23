.. _initscript:

The NICOS init.d script
=======================

For Unix systems, NICOS provides a ``init.d`` script in ``etc/nicos-system``
which is by default linked into ``/etc/init.d``.

The init script manages all the NICOS services configured in ``nicos.conf`` (see
below).  It supports the usual commands such as ::

  /etc/init.d/nicos-system start
  /etc/init.d/nicos-system stop
  /etc/init.d/nicos-system status
  /etc/init.d/nicos-system restart

to be started automatically by the system's startup mechanism.

However, it also can manage one individual service by giving the name after the
command, such as ::

  /etc/init.d/nicos-system restart poller

The init script determines the instrument from the first of these sources:

* The ``INSTRUMENT`` environment variable
* An ``INSTRUMENT=inst`` line in ``/etc/default/nicos-system``
* The default mechanism of the NICOS services, i.e. the "middle part" of
  hostname of the system (``machine.instrument.tld``)


Configuration
-------------

In your ``nicos.conf`` file (which should be at the root of the NICOS
installation directory), there is a header ``[services]`` with the same key that
configures the init script::

  [services]
  services = cache,poller,elog,watchdog,daemon,monitor-html

If an entry consists of ``service-instancename``, like in ``monitor-html``
above, the service is started with the instancename as an argument.  In this
case, that starts the monitor with ``html`` as an argument, which subsequently
loads the ``monitor-html.py`` setup instead of the ``monitor.py`` setup.

A graphical NICOS monitor should not be started with the initscript: the
processes are meant to be started with root permissions by the init system (and
then change their user as part of becoming a daemon), which does not work well
with an X client application.
