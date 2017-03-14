.. index:: !poller, !nicos-poller
.. _poller:

The Poller daemon
=================

The poller is a service that queries volatile information such as current sensor
and motor readings from all devices in the instrument setup, and pushes updates
to the NICOS cache.

The main poller process is a supervisor that manages a bunch of subprocesses,
one for each setup that is polled.  When one of the subprocesses dies
unexpectedly, it is restarted automatically.  Within the subprocess, each
device is polled in its own thread.


Invocation
----------

The poller is invoked by the ``nicos-poller`` script.  It should normally be
started by the :ref:`init script <initscript>`.

The poller expects a setup file with a device named ``Poller``.

.. The file must be named either ``poller.py`` or :file:`SETUPNAME.py`, where
   ``SETUPNAME`` is a user-defined name.

On startup using the ``nicos-poller`` executable, the setup loaded is either
``poller.py`` if started with no arguments, or ``SETUPNAME.py`` if started
with command line arguments ``-S`` or ``--setup``.

There are several command-line options that allow to customize the startup of
the poller.

.. program:: poller

.. option:: -h, --help

   show the help message and exit

.. option:: -d, --daemon

   daemonize the poller process

.. option:: -S SETUPNAME, --setup=SETUPNAME

   name of the setup, default is 'poller'

Setup file
----------

The setup file for the poller service is by default:
``custom/<instrument_name>/setups/special/poller.py``.

A simple setup file for the poller could look like this::

  description = 'setup for the poller'
  group = 'special'

  sysconfig = dict(
    cache = 'localhost'
  )

  devices = dict(
      Poller = device('services.poller.Poller',
                      autosetup = True,
                      poll = [],
                      alwayspoll = ['reactor'],
                      neverpoll = ['detector'],
                      blacklist = [],
                     ),
  )

The cache to connect to must be given in the ``sysconfig`` dictionary entry::

  cache = 'host:port'

where the default port of the cache service is used if the port is omitted.

The poller device has several parameters, none of which must be specified.

Server class
------------

.. module:: nicos.services.poller

.. autoclass:: Poller()

.. todo::

   Inconsistencies between class doc and added doc for:

   - autosetup
   - poll
   - alwayspoll

**autosetup**
  If true (the default), the poller automatically starts subprocesses for each
  setup loaded in the NICOS :term:`master`.  If false, no processes are started
  unless configured with ``poll`` or ``alwayspoll``.

**poll**
  A list of setups whose devices should be polled, if loaded in the NICOS
  master.

**alwayspoll**
  A list of setups whose devices should be polled regardless of what is loaded
  in the NICOS master.

**neverpoll**
  A list of setups whose devices should not be polled, even if ``autosetup`` is
  true and the setups are loaded in the master.

**blacklist**
  A list of **devices** that should never be polled even if the setups they
  appear in are polled.

  .. note::

    This should be used for devices that do not allow concurrent connections
    from the NICOS master and the poller processes.  (Although the master
    should use the values acquired by the poller via cache instead of asking
    the hardware, this may not always work due to timing.)
