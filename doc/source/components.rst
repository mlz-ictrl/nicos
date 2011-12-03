.. _components:

==============================
Components of the NICOS system
==============================

These are the executable scripts in ``bin/``:

**Shells**

These components allow the user -- in some form or other -- to interact with the
NICOS system and execute commands.

``nicos-console``
  This is the most basic NICOS shell.  It presents to the user a slightly
  enhanced builtin Python shell, where commands can be executed.

``nicos-web``
  This is a web-frontend version of the NICOS console.  It implements a simple
  web server that presents a console-like user interface via the web browser.

``nicos-ipython``
  This is a version of ``nicos-console`` that uses the IPython shell instead of
  the builtin Python shell.

``nicos-gui``
  This is the GUI client part of the server-client execution shell.  It connects
  to a ``nicos-daemon`` instance (see below).  The GUI requires PyQt4 for the
  basic functionality, and PyQwt5 for the data plotting and scans windows.


**Other clients**

These programs are clients that don't provide shell functionality.

``nicos-monitor``
  This program implements a graphical status monitor that displays current
  values from the NICOS cache.


**Daemons**

These programs provide services and are designed to run as daemons once per
instrument.

``nicos-cache``
  The NICOS cache collects all values and parameters read from NICOS devices, so
  that individual components do not need to access the hardware too often.  It
  also serves as an archival system for the instrument status.  For situation
  where excessive caching is not required, NICOS can also run without the cache
  component.

``nicos-daemon``
  This is the server part of the server-client execution shell.  It can be
  controlled via a TCP connection using a custom protocol designed for this
  purpose.  Multiple GUI clients can connect to one daemon.

``nicos-poller``
  The poller periodically queries volatile information from all devices in the
  current instrument setup, and pushes updates to the NICOS cache.

``nicos-elog``
  This daemon provides the "electronic logbook".  It collects information about
  special events such as "new sample" or "scan finished", and writes them to
  disk in a HTML file, which can serve as an electronic logbook of the
  experiment that is easier to read than a mere logfile.
