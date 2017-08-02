.. _nicosconf:

The ``nicos.conf`` configuration file
=====================================

At startup, all NICOS processes read a file called ``nicos.conf``; it should be
located in the "root" directory of the NICOS installation, i.e. the directory
containing the ``nicos`` package directory.

Additionally, a file with specific settings for an instrument is expected in
``nicos_<facility>/<instrument>/nicos.conf`` and will be loaded automatically.

The facility and instrument can either be specified by an ``INSTRUMENT``
environment variable (for example, ``INSTRUMENT=nicos_demo.demo``), or in the
"root" ``nicos.conf`` file (see below).

The file ``nicos.conf`` is an INI-style configuration file.  It contains only
the most basic configuration for the whole NICOS system; all further
configuration is done in setup files, see :ref:`setups`.

The possible entries are:

Section ``[nicos]``
-------------------

  * ``setup_package`` -- a Python package to look for the facility-specific
    setup directories; the package will be searched for in ``PYTHONPATH``.

  * ``instrument`` -- the instrument name inside the ``setup_package`` to find
    the instrument specific ``nicos.conf``.  Note: when ``setup_package`` is
    known, it may provide a way to autodetect the instrument (e.g. at MLZ, the
    instrument can be found from the middle part of the hostname).

  * ``setup_subdirs`` -- the subdirectories of the ``setup_package`` with setups
    to use, separated by ``,`` (e.g. ``panda,frm2``).

  * ``user`` -- system user to use when becoming a daemon.
  * ``group`` -- system group to use when becoming a daemon.
  * ``logging_path`` -- the root path for all NICOS related log files, by
    default the ``log/`` directory in the installation root will be used.
  * ``pid_path`` -- the path for NICOS service to place PID files while they
    are running, by default ``pid/`` in the installation root will be used.

  * ``services`` -- a comma-separated list of NICOS daemons to start and stop
    with the provided :ref:`init script <initscript>`. If ``none`` is specified,
    no services will be started. This is useful as a fallback and for getting
    nicos up and running.

  * ``services_<hostname>`` -- a comma-separated list of NICOS daemons to start
    and stop with the provided :ref:`init script <initscript>` running on host
    <hostname> (short name as output by `hostname -s`). If the script is executed
    on a host for which there is no such entry, the entry ``services`` is used as
    a fallback.

  * ``sandbox_simulation`` -- if set to "true" or "1", NICOS simulation
    processes will be sandboxed (they have no write access to the filesystem,
    and no network access).  This requires a Linux system with kernel >= 2.6.32.
    Default is off.


Section ``[environment]``
-------------------------

  Any key will be taken as the name of an environment variable and set in the
  NICOS process' environment.  For example, this is useful to set ``NETHOST``
  for TACO, or ``PYTHONPATH`` to find additional Python modules.
  If you want to amend the environment variable instead of replacing the value,
  refer to the old value as ``$<VARNAME>``, e.g.
  ``LD_LIBRARY_PATH=/some/dir:$LD_LIBRARY_PATH``. To keep the ``$`` in
  the environment variable, escape it as ``$$``.
