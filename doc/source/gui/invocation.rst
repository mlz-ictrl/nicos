GUI invocation
==============

The NICOS GUI is invoked with the ``nicos-gui`` script.

Usage of the script::

   nicos-gui [options] [username@server [password]]

The script has several options:

-h, --help                    show the help message and exit
-c file, --config-file file   use ``file`` as the configuration file

Apart from the options, you can also give one or two arguments: the first is a
"connection string" consisting of ``username@server`` (server can be a host name
or ``hostname:port``), the second can be the password for connecting (if the
password is not given, the user will be asked).

If both connection string and password are given, the client connects
automatically on startup.

Log file
--------

The NICOS GUI writes a log file with all unhandled tracebacks that are printed
to the console in abbreviation.  The log file can be found in
``~/.config/nicos/log``.

Configuration
-------------

For configuration of the interface please see :ref:`gui-config`.
