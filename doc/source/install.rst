Installing NICOS
================

Get the source code
-------------------

NICOS is maintained in a Git repository hosted at the FRM II.  You can clone
this repository using ::

  git clone git://forge.frm2.tum.de/home/repos/git/frm2/nicos/nicos-core.git

Alternatively you can get the current snapshot from

  http://forge.frm2.tum.de/cgit/cgit.cgi/frm2/nicos/nicos-core.git/snapshot/nicos-core-master.tar.bz2

For development, we use SSH access via Gerrit::

  git clone ssh://forge.frm2.tum.de:29418/frm2/nicos/nicos-core.git

Note that you have to log in once at the `FRM II Gerrit instance
<http://forge.frm2.tum.de/review/>`_ and add a public key for SSH, since only
public key authentication is enabled.

The bug tracker and project wiki are at

  https://forge.frm2.tum.de/projects/nicos/


.. _requirements:

Requirements
------------

* At least Python 2.7 or Python 3.3

If not mentioned otherwise, Python packages are available from PyPi (https://pypi.python.org/pypi)

* NICOS specific Python packages (available from http://forge.frm2.tum.de/simple)

  - nicos-pyctl
  - nicos-quickyaml

* Required Python packages

  - numpy
  - pyzmq version >= 2

* For the provided SysV compatible init script

  - psutil version >= 0.4 (recommended >= 2.0)

* For hardware access (optional):

  - the MLZ TACO Python libraries (See https://forge.frm2.tum.de/wiki/projects:software_distribution)
  - pyserial (for TACO-less serial line communication)
  - pyepics (for epcis interface)
  - a working installation of omniORBpy (http://omniorb.sourceforge.net/) (for CARESS interface)
  - PyTango8 (for TANGO interface, needs TANGO libraries)

* Optional for the basic system:

  - scipy (for data fitting)
  - docutils (for formatting interactive help nicely)
  - matplotlib (for resolution plots)
  - gnuplot (for plots in the electronig logbook)
  - Grace (for scanplot)
  - mysql-connector-python (preferred) or MySQLdb (for proposal DB query)
  - lxml (for U-Bahn service)
  - pyfits (for the handling of FITS formatted files)
  - rsa (for encrypted daemon authentication)
  - ldap3 (for ldap authentication)
  - sendsms tool to use the SMS notifier (See: http://smslink.sourceforge.net/)

* For the GUI and status monitor (Due to limitations in the used graphics
  libraries, only Python2 (>=2.7.4) is supported):

  - PyQt4 (not installable with pip)
  - gr (optional, for plots)
  - PyQwt (optional, for the transition period as an alternative to gr, for plots)
    (not installable with pip)
  - QScintilla-python (optional, for the script editor component)
    (not installable with pip)
  - scipy (optional, for fitting)
  - nicos-livewidget (optional, for detector live view, available from
    http://forge.frm2.tum.de/simple)
  - cfitsio (optional, required by nicos-livewidget, this not a Python package)
  - python-redmine (optional, for the bug reporting dialog)

* For development (running tests, generating documentation):

  - nose
  - mock
  - coverage (optional)
  - sphinx (for generating doc)

* Under Windows:
  - pyreadline (optional, for the console to work)
  - colorama (optional, for colored console output)

If not supplied by the distribution (see below), most dependencies
(except PytQt, PyQwt, sip) can be installed from the
python package repository: ::

  pip install -r requirements.txt

pip can be obtained from https://pip.pypa.io/en/stable/news/

For xBuntu 12.04: install pip ::

  sudo apt-get install python-pip

If your system pip is too old (pip >=1.4 is required) you can update with: ::

  sudo pip install --upgrade pip
  hash -r


Packages to install for common distributions
--------------------------------------------

xBuntu 12.04
^^^^^^^^^^^^

* Basic system:

  apt-get install python python-{dev,zmq,numpy,scipy,psutil} gnuplot

* Optional components:

  apt-get install python-{mysqldb,docutils,serial,matplotlib,pyfits,lxml,ldap3,rsa,mysql.connector}

* GUI and status monitor:

  apt-get install python-{qt4,qwt5-qt4,qscintilla2}

* Development and documentation build:

  apt-get install python-{sip-dev,qt4-dev,nose,mock,coverage,sphinx}

* For the livewidget you have to install some development packages:

  apt-get install libqwt5-qt4-dev libtiff5-dev libcfitsio3-dev



Configure for experimenting
---------------------------

Now you can start the individual :ref:`components <components>`.  A setup that
uses all the major components can be started using ::

  bin/nicos-demo

This starts the cache, poller, electronic logbook, and daemon services, and also
starts the graphical interface and a status monitor.

The console will load the demo setups from ``custom/demo/setups``.  The startup
setup contains a few devices that show basic usage of the NICOS system.  Call
``help()`` to get a list of commands.  You can also call ``help(dev)`` to get
help for an individual device.

.. You can continue with :ref:`the first steps <firststeps>` from here.


Configure and build the distribution at an instrument
-----------------------------------------------------

.. todo::

   this needs to be changed!

For specific instruments, we will set up a set of setups and customizations for
that instrument.  When this is done, the installation process looks like this::

  cd nicos-core
  make
  [sudo] make install INSTRUMENT=<instrument name>


The customization is located in a subdirectory of ``custom/``.  It contains a
file called ``nicos.conf`` that tells the NICOS how the system shall behave (see
:ref:`nicosconf`).


.. _nicosconf:

The ``nicos.conf`` configuration file
-------------------------------------

At startup, all NICOS processes read a file called ``nicos.conf``; it should be
located in the "root" directory of the NICOS installation, i.e. the directory
containing the ``__init__.py`` main file.

A file with default settings for each instrument is expected in
``custom/instrumentname/nicos.conf`` and will be loaded automatically.  The
instrument can either be specified implicitly by the middle part of the
fully-qualified hostname, given by an ``INSTRUMENT`` environment variable, or in
the "root" ``nicos.conf`` file (see below).

The file ``nicos.conf`` is an INI-style configuration file.  It contains only
the most basic configuration for the whole NICOS system; all further
configuration is done in setup files, see :ref:`setups`.  For existing
customizations, the file will automatically be generated by the Makefile.

The possible entries are:

* Under the section ``[nicos]``:

  * ``instrument`` -- the instrument name to find the instrument specific
    ``nicos.conf`` (if not guessable from the hostname)
  * ``custom_paths`` -- paths (separated by ``:``) to look for the "custom"
    directory (with instrument-specific libs and setups); the first one that
    exists will be used
  * ``setup_subdirs`` -- the subdirectories of the custom path with setups to
    use, separated by ``,`` (e.g. ``panda,frm2``)
  * ``user`` -- system user to use when becoming a daemon
  * ``group`` -- system group to use when becoming a daemon
  * ``logging_path`` -- the root path for all NICOS related log files, by
    default the ``log/`` directory in the installation root will be used

  * ``services`` -- a comma-separated list of NICOS daemons to start and stop
    with the provided :ref:`init script <initscript>`. If ``none`` is specified,
    no services will be started. This is useful as a fallback and for getting
    nicos up and running.

  * ``services_<hostname>`` -- a comma-separated list of NICOS daemons to start
    and stop with the provided :ref:`init script <initscript>` running on host
    <hostname> (short name as output by `hostname -s`). If the script is executed
    on a host for which there is no such entry, the entry ``services`` is used as
    a fallback.

* Under the section ``[environment]``:

  Any key will be taken as the name of an environment variable and set in the
  NICOS process' environment.  For example, this is useful to set ``NETHOST``
  for TACO, or ``PYTHONPATH`` to find additional Python modules.
