.. index:: !elog, !nicos-elog
.. _elog:

The Electronic Logbook daemon
=============================

The electronic logbook ("elog") is a service that collects information about
special events such as "new sample" or "scan finished", and writes them to disk
in an HTML file, which can serve as an electronic logbook of the experiment that
is easier to read than a mere plain-text logfile.

The HTML files are written in the current data directory, in a subdirectory
named ``logbook``.


Invocation
----------

The elog is invoked by the ``nicos-elog`` script.  It should normally be started
by the :ref:`init script <initscript>`.

The elog expects a setup file named ``elog.py`` with a device named ``Logbook``.

There are several command-line options that allow to customize the startup of
the elog.

.. program:: elog

.. option:: -h, --help

   show the help message and exit

.. option:: -d, --daemon

   daemonize the elog process

If you want to use the electronic logbook, make sure the "system" setup for the
NICOS master has also a cache configured, and the ``elog`` parameter of the
experiment object is true.


Setup file
----------

The setup file for the electronic logbook daemon is by default:
``custom/<instrument_name>/setups/special/elog.py``.

A simple setup file for the poller could look like this::

  description = 'setup for the electronic logbook'
  group = 'special'

  devices = dict(
      Logbook = device('nicos.services.elog.Logbook',
                       cache = 'localhost:14869',
                      ),
  )

The :class:`Logbook <nicos.services.elog.Logbook>` device has only one important
parameter, the *cache* to connect to.

Server class
------------

.. module:: nicos.services.elog

.. autoclass:: Logbook()
