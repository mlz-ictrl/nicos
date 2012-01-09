Installing NICOS
================

Get the source code
-------------------

NICOS is maintained in a Git repository hosted at the FRM II.  You can clone
this repository using ::

  git clone git://trac.frm2.tum.de/home/repos/git/frm2/nicos/nicos-core.git

Alternatively you can get the current snapshot from

  http://trac.frm2.tum.de/cgit/cgit.cgi/nicos/nicos-core.git/snapshot/nicos-core-master.tar.bz2

For development, we use SSH access via Gerrit::

  git clone ssh://trac.frm2.tum.de:29418/frm2/nicos/nicos-core.git

Note that you have to log in once at the `FRM II Gerrit instance
<http://trac.frm2.tum.de/review/>`_ and add a public key for SSH, since only
public key authentication is enabled.

The bug tracker and project wiki are at

  https://trac.frm2.tum.de/projects/NICOS/


Requirements
------------

* At least Python 2.5

* For the basic system:

  - numpy
  - the TACO Python libraries (optional)
  - scipy (optional, for fitting and data analysis)
  - gnuplot-py (optional, for liveplot display in gnuplot)
  - MySQLdb (optional, for proposal DB query)
  - python-xmpp (optional, for Jabber notifications)
  - pyserial (optional, for TACO-less serial line communication)

* For the status monitor: one of PyQt4, PyGTK, PyFLTK or Tkinter

* For the client-server GUI:

  - PyQt4
  - numpy
  - PyQwt (optional, for liveplot display)
  - scipy (optional, for fitting)

.. * For the client-server text UI:   (which doesn't currently work)

  - urwid


Configure and build in-place for experimenting
----------------------------------------------

For development and testing purposes, NICOS components can be run directly from
the source directory.  For this, you have to build the C modules once using
``make inplace``::

  cd nicos-core
  make inplace

Now you can start the individual :ref:`components <components>`.  A minimal
setup that uses all the major components can be started using ::

  bin/nicos-cache &
  bin/nicos-poller &
  bin/nicos-console

The console will load the test setups from ``custom/test/setups``.  The startup
setup contains a few devices that show basic usage of the NICOS system.  Call
``help()`` in the console to get a list of commands, and ``listdevices()`` to
get a list of devices that can be manipulated.  You can also call ``help(dev)``
to get help for an individual device.

You can continue with :ref:`the first steps <firststeps>` from here.


Configure and build the distribution at an instrument
-----------------------------------------------------

For specific instruments, we will set up a set of setups and customizations for
that instrument.  When this is done, the installation process looks like this::

  cd nicos-core
  make
  [sudo] make install INSTRUMENT=<instrument name>

The configuration will be installed as ``/opt/nicos/setups`` by default, but
that is also configurable for each instrument.
