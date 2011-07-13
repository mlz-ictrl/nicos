.. _components:

==============================
Components of the NICOS system
==============================

These are the executable scripts in ``bin/``:

**Command and script execution components**

``nicos-console``
  This is the most basic NICOS component.  It presents to the user a slightly
  enhanced builtin Python shell, where commands can be executed.

``nicos-web``
  This is a web-frontend version of the NICOS console.  It implements a simple
  web server that presents a console-like user interface via the web browser.

``nicos-ipython``
  This is a version of ``nicos-console`` that uses the IPython shell instead of
  the builtin Python shell.

``nicos-daemon``
  This is the server part of the server-client execution component.  It can be
  controlled via a TCP connection using a custom protocol designed for this
  purpose.

``nicos-gui``
  This is the GUI client part of the server-client execution component.  It
  requires PyQt4 for the basic functionality, and PyQwt5 for the data plotting
  and analysis windows.


**Other components**

``nicos-cache``
  The NICOS cache collects all values and parameters read from NICOS devices, so
  that individual components do not need to access the hardware too often.  It
  also serves as an archival system for the instrument status.  For situation
  where excessive caching is not required, NICOS can also run without the cache
  component.

``nicos-poller``
  The poller periodically queries volatile information from all devices in the
  current instrument setup, and pushes updates to the NICOS cache.

``nicos-monitor``
  This script implements a graphical status monitor that displays current values
  from the NICOS cache.
