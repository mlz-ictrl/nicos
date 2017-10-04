GUI invocation
==============

The NICOS GUI is invoked with the ``nicos-gui`` script.

Usage of the script::

   nicos-gui [options] [user_name[:password[@host[:port]]]]

The script has several options:

-h, --help                    show the help message and exit
-c file, --config-file file   use ``file`` as the configuration file
-v, --view-only               run in view-only mode

Apart from the options, you can also give an argument: the "connection string"
consisting of  ``user_name``, ``password``, ``host``, and ``port``.

If the "connection string" contains the user_name, password and host, the client
connects automatically on startup, otherwise the user will be asked for missing
parts of the "connection string".

Log file
--------

The NICOS GUI writes a log file with all unhandled tracebacks that are printed
to the console in abbreviation.  The log file can be found in
``~/.config/nicos/log``.

Configuration
-------------

For configuration of the interface please see :ref:`gui-config`.
