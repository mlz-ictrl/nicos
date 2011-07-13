Installing NICOS-ng
===================

Get the source code
-------------------

::

  git clone git://trac.frm2.tum.de/home/repos/git/frm2/nicos/nicos-core.git

or (using SSH with public-key authentication)::

  git clone ssh://trac.frm2.tum.de:29418/frm2/nicos/nicos-core.git

Alternatively you can get the current snapshot from::

  http://trac.frm2.tum.de/cgit/cgit.cgi/nicos/nicos-core.git/snapshot/nicos-core-master.tar.bz2


Configure and build in-place for experimenting
----------------------------------------------

::

  cd nicos-core
  make inplace

Now you can start the individual :ref:`components <components>`.  A minimal
setup that uses all the major components can be started using ::

  bin/nicos-cache &
  bin/nicos-poller &
  bin/nicos-console

The console will load the test setups from ``custom/test/setups``.  The startup
setup contains a few devices that show basic usage of the NICOS system.  Call
``help()`` in the console to get a list of commands, and ``ListDevices()`` to
get a list of devices that can be manipulated.


Configure and build the distribution at an instrument
-----------------------------------------------------

::

  cd nicos-core
  make
  [sudo] make install INSTRUMENT=<instrument name>

The configuration will be installed as ``/opt/nicos/setups`` by default.


Requirements
------------

* At least Python 2.6

* For the basic system:
  - numpy
  - the TACO Python libraries (optional)
  - scipy (optional, for fitting)
  - gnuplot-py (optional, for liveplot display in gnuplot)
  - MySQLdb (optional, for proposal DB query)
  - python-xmpp (optional, for Jabber notifications)
  - pyserial (optional, for TACO-less serial line communication)

* For the status monitor: one of
  - PyQt4
  - PyGTK
  - PyFLTK
  - Tkinter

* For the client-server GUI:
  - PyQt4
  - numpy
  - PyQwt (optional, for liveplot display)
  - scipy (optional, for fitting)

* For the client-server text UI:
  - urwid
