.. index:: !collector, !nicos-collector
.. _collector:

The Collector daemon
====================

The collector service enables cache update forwarding.

Invocation
----------

The collector is invoked by the ``nicos-collector`` script.  It should normally
be started by the :ref:`system startup integration <sys-startup>`.

The collector expects a setup file with a device named ``Collector``.

On startup using the ``nicos-collector`` executable, the setup loaded is either
``collector.py`` if started with no arguments, or ``SETUPNAME.py`` if started
with command line arguments ``-S`` or ``--setup``.

There are several command-line options that allow to customize the startup of
the collector.

.. program:: nicos-collector

.. option:: -h, --help

    show the help message and exit

.. option:: -d, --daemon

    daemonize the collector process

.. option:: -S SETUPNAME, --setup=SETUPNAME

    name of the setup, default is 'collector'


Setup file
----------

The setup file for the cache service is by default:
``<setup_package>/<instrument_name>/setups/special/collector.py``.

A simple setup file for the collector putting data received and filtered from
a remote system into a target system could look like this::

  description = 'setup for the NICOS collector'
  group = 'special'

  devices = dict(
      TargetCache = device('nicos.services.collector.CacheForwarder',
          cache = 'targethost:14869',
          prefix = 'nicos/remotesys/',
      ),
      Collector = device('nicos.services.collector.Collector',
          cache = 'sourcehost:14869',
          forwarders = ['TargetCache'],
          keyfilters = ['selector.*'],
      ),
  )

The main device ("Collector") has a ``cache`` parameter that defines the
network address which it connects to (in our case ``sourcehost:14869``).

The ``keyfilters`` defines that only keys starting with ``selector`` are
forwarded into the cache defined in the ``TargetCache`` device parameter
``cache``.

The forwarding device ``TargetCache`` transfers all received and filtered
data from the cache defined in the ``cache`` and the ``keyfilter``
parameters of the ``Collector`` device. The target cache is defined in the
``cache`` parameter of the ``TargetCache``.

.. seqdiag::

   seqdiag {
        autonumber = True;

        "source host cache" -> Collector [label="cache event"];
        Collector -> TargetCache [ label="filter event"];
        TargetCache --> "target host cache" [leftnote="filtering successful", label="put key value pair"];
   }


Server class
------------

.. module:: nicos.services.collector

.. autoclass:: Collector()


Forwarders
----------

.. autoclass:: CacheForwarder()

.. autoclass:: WebhookForwarder()
