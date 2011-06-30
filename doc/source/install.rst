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


Configure and build the distribution
------------------------------------

::

  cd nicos-core
  make
  [sudo] make install INSTRUMENT=<instrument name>

The configuration will be installed as ``/opt/nicos/setups`` by default.
