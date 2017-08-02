Installing NICOS
================

Get the source code
-------------------

NICOS is maintained in a Git repository hosted at the FRM II.  You can clone
this repository using ::

  git clone https://forge.frm2.tum.de/review/frm2/nicos/nicos-core

Alternatively you can get the current snapshot from

  http://forge.frm2.tum.de/cgit/cgit.cgi/frm2/nicos/nicos-core.git/snapshot/nicos-core-master.tar.bz2

For development, we use SSH access via Gerrit::

  git clone ssh://forge.frm2.tum.de:29418/frm2/nicos/nicos-core.git

Note that you have to log in once at the `FRM II Gerrit instance
<http://forge.frm2.tum.de/review/>`_ and add a public key for SSH, since only
public key authentication is enabled.

The bug tracker and project wiki are at

  https://forge.frm2.tum.de/projects/nicos/


.. include:: ../../INSTALL


Configure for experimenting
---------------------------

Now you can start the individual :ref:`components <components>`.  A setup that
uses all the major components can be started with the single command::

  bin/nicos-demo

This starts the cache, poller, electronic logbook, and daemon services, and also
starts the graphical interface and a status monitor.

It will load the demo setups from ``nicos_demo/demo/setups``.  The startup setup
contains a few devices that show basic usage of the NICOS system.  Call
``help()`` to get a list of commands.  You can also call ``help(dev)`` to get
help for an individual device.

.. You can continue with :ref:`the first steps <firststeps>` from here.


Configure and build the distribution
------------------------------------

You can use ``make install PREFIX=/some/prefix`` to install NICOS into a
directory.  The target also supports ``DESTDIR`` for building packages.

The toplevel ``nicos.conf`` file (see :ref:`nicosconf`) is searched in
that directory.
