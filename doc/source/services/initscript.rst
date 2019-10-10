.. _sys-startup:

NICOS system startup integration
================================

The startup integration manages all the NICOS services configured in
``nicos.conf`` (see below).

For Unix systems, NICOS provides a ``init.d`` script in ``etc/nicos-system``
which is by default linked into ``/etc/init.d``.

For modern Linux sytems, systemd services are provided instead.

Both startup systems determine the instrument from the first of these sources:

* The ``INSTRUMENT`` environment variable
* An ``INSTRUMENT=inst`` line in ``/etc/default/nicos-system``
* The default mechanism of the NICOS services, i.e. the "middle part" of
  hostname of the system (``machine.instrument.tld``)


Init script
-----------

The init script supports the usual commands such as ::

  /etc/init.d/nicos-system start
  /etc/init.d/nicos-system stop
  /etc/init.d/nicos-system status
  /etc/init.d/nicos-system restart

to be started automatically by the system's startup mechanism.

However, it also can manage one individual service by giving the name after the
command, such as ::

  /etc/init.d/nicos-system restart poller


Systemd services
----------------

Since the services to start can be configured depending on the hostname, NICOS
generates ``.service`` unit files on the fly, using a single
``nicos-late-generator.service`` unit.  To install the systemd integration,
you have to move or symlink these files in place:

* ``etc/nicos-late-generator`` to ``/lib/systemd/scripts``
* ``etc/nicos-late-generator.service`` to ``/lib/systemd/system``
* ``etc/nicos.target`` to ``/lib/systemd/system``

Then ``systemd enable`` only ``nicos-late-generator.service``.

The generator service will run during the boot process and do the following:

* Apply the configuration from the :ref:`nicos.conf file <nicosconf>`
* Wait (with some timeout) for a system hostname to be known
* Check with services should be started on the host
* Create corresponding ``nicos-XXX.service`` files under ``run/systemd/system``
* Add them all as dependencies of ``nicos.target``
* Start ``nicos.target``

This should result in all configured services being started and supervised
by systemd.


Configuration
-------------

In your ``nicos.conf`` file (which should be at the root of the NICOS
installation directory), there is a header ``[services]`` that configures the
startup system::

  [services]
  services = cache,poller,elog,watchdog,daemon,monitor-html

If an entry consists of ``servicename-instancename``, like in ``monitor-html``
above, the service is started with the instancename as an argument.  In this
case, that starts the monitor with ``html`` as an argument, which subsequently
loads the ``monitor-html.py`` setup instead of the ``monitor.py`` setup.

There can be additional keys called ``services_<hostname>``, which activate
the given services only on a host with that name.

A graphical NICOS monitor should not be started with startup system: the
processes are meant to be started with root permissions by the init system (and
then change their user as part of becoming a daemon), which does not work well
with a graphical application.
