.. index:: !cache, !nicos-cache
.. _cache:

The Cache daemon
================

The NICOS cache is a service that collects all values and parameters read from
NICOS devices, so that individual components do not need to access the hardware
too often.  It also serves as an archival system for the instrument status.

For situation where excessive caching is not wanted, NICOS can also run without
the cache component.  However, several other services such as the electronic
logbook and the watchdog depend on a running cache, as it is their means of
inter-process data exchange.


Invocation
----------

The cache is invoked by the ``nicos-cache`` script.  It should normally be
started by the :ref:`init script <initscript>`.

The cache expects a setup file with a device named ``Server``.

.. The file must be named either :file:`SETUPNAME.py`, where ``SETUPNAME`` is a
   user-defined name, given by the ``-S, --setup`` command line option or
   ``cache.py`` if the ``nicos-cache`` is started without a given setup name.

On startup using the ``nicos-cache`` executable, the setup loaded is either
``cache.py`` if started with no arguments, or ``SETUPNAME.py`` if started
with command line arguments ``-S`` or ``--setup``.

There are several command-line options that allow to customize the startup of
the cache.

.. program:: cache

.. option:: -h, --help

    show the help message and exit

.. option:: -d, --daemon

    daemonize the cache process

.. option:: -S SETUPNAME, --setup=SETUPNAME

    name of the setup, default is 'cache'


Setup file
----------

The setup file for the cache service is by default:
``custom/<instrument_name>/setups/special/cache.py``.

A simple setup file for the cache could look like this::

  description = 'setup for the cache server'
  group = 'special'

  devices = dict(
      DB     = device('services.cache.server.FlatfileCacheDatabase',
                      storepath = 'data/cache',
                     ),

      Server = device('services.cache.server.CacheServer',
                      db = 'DB',
                      server = 'localhost',
                     ),
  )

The main device ("Server") has a ``server`` parameter that defines the network
address on which the cache listens.
The setup shows the cache is listening at ``localhost:14869`` since the default
port is ``14869``.

There is an attached device for the server, the cache database.  In our example
it is a :class:`FlatfileCacheDatabase <nicos.services.cache.database.FlatfileCacheDatabase>`,
which stores the data under directory ``data/cache`` in the current directory.

There are :ref:`several database classes <cache_databases>` that can be used
here.


Server class
------------

.. module:: nicos.services.cache.server

.. autoclass:: CacheServer()


Cache databases
---------------

.. _cache_databases:

.. module:: nicos.services.cache.database

.. autoclass:: FlatfileCacheDatabase()

.. autoclass:: MemoryCacheDatabase()

.. autoclass:: MemoryCacheDatabaseWithHistory()


For a documentation of the network protocol of the cache, please see
:doc:`/protocols/cache`.
