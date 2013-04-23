===================
The daemon protocol
===================

Basics
======

The daemon protocol consists of two socket connections: the command connection
and the event connection.  The command connection is used in a request-reply
mode, while the event connection is read-only for the client.

Frame format
------------

**Command connection**

A data frame on the command connection has one of three types: "ok", "error" or
"data".  The first byte selects the type with the ASCII values ACK (0x6), NAK
(0x15) and STX (0x2) respectively.

"ok" frames have no further content; they consist of only one byte.

For "error" and "data" frames, the following four bytes encode the length of the
payload (i.e. frame length excluding first byte and length) as a network-order
(big-endian) unsigned 32-bit integer.

For "error" frames, the payload is a simple string explaining the error.

For "data" frames sent from the daemon to the client, the payload is a
serialized Python object.

For "data" frames sent from the client to the daemon (commands), the command is
separated from arguments by ASCII value RS (0x1E).  There can be any number of
arguments separated by RS, as long as the command accepts them.  Arguments are
not serialized, so only strings are allowed.

**Event connection**

On this connection, all data flows from daemon to client.  Frames look like a
"data" frame on the command connection, with the event name and one data item
separated by RS.

For most events, the data is a serialized Python object, except for those where
a lot of raw data has to be transferred, such that serialization is both slow
and unnecessary.  In the Events_ documentation, unserialized transfer of data is
noted where applicable.

Serialization
-------------

Serialization format is Python pickle format 2.

Handshake
---------

First, a client must generate a random 32-byte ID used as the client ID (e.g.
the MD5 of the host name and the current time, or 32 bytes of urandom data).

Open a connection to the server port and send the client ID.  The daemon will
check if the connecting host is allowed to connect, and then send a data frame
with a serialized dictionary with at least the following keys:

* ``daemon_version`` -- the NICOS version string of the daemon (mostly for
  informational purposes in the client)
* ``protocol_version`` -- the version of the daemon protocol: if the version on
  client side doesn't match, the client should close the connection
* ``pw_hashing`` -- the method of transferring passwords, either 'md5', 'sha1'
  or 'plain'; the client should hash passwords with the given algorithm (except
  if it is 'plain') before sending

The daemon then expects a data frame with three strings (separated by RS),
giving the login name, the password (possibly hashed) and a string to use as the
:envvar:`DISPLAY` environment variable on the server.  The latter is mostly
obsolete, as it is incompatible with logins from multiple machines; no value
needs to be transferred.

If the login name and password are accepted, the daemon sends back an "ok" frame
and connection is ready to accept commands.

At this time, the client can open a second connection to the server port and
send the client ID.  This connection will be detected as the event connection,
and the client can then start receiving data frames on this connection.

Commands
========

These commands can be sent over the command socket.

Script commands
---------------

.. daemoncmd:: queue
.. daemoncmd:: start
.. daemoncmd:: unqueue
.. daemoncmd:: update

Control flow commands
---------------------

.. daemoncmd:: break
.. daemoncmd:: continue
.. daemoncmd:: stop
.. daemoncmd:: emergency

Information requests
--------------------

.. daemoncmd:: getstatus
.. daemoncmd:: getmessages
.. daemoncmd:: getscript
.. daemoncmd:: getdataset
.. daemoncmd:: gettrace

Asynchronous code execution
---------------------------

.. daemoncmd:: exec
.. daemoncmd:: eval
.. daemoncmd:: simulate

Cache interaction
-----------------

.. daemoncmd:: gethistory
.. daemoncmd:: getcachekeys

Watch expressions
-----------------

.. daemoncmd:: watch
.. daemoncmd:: unwatch

Miscellaneous auxiliary commands
--------------------------------

.. daemoncmd:: complete
.. daemoncmd:: eventmask
.. daemoncmd:: getversion
.. daemoncmd:: transfer

Experimental commands
---------------------

.. daemoncmd:: debug
.. daemoncmd:: debuginput

Terminating a connection
------------------------

.. daemoncmd:: unlock
.. daemoncmd:: quit


Events
======

These are the events emitted by the daemon and transferred on the event
connection.  The data is serialized (using pickle, see Serialization_) unless
noted.

.. daemonevt:: message

   A new log message has been emitted.

   :arg: The new message, as a list with the following members:

      - source logger name
      - message time as Unix timestamp
      - message level as a number
      - message text
      - exception traceback if present
      - message prefix (normally empty, but can be selected different for
        simulation output, see `simulate`)

.. daemonevt:: request

   A new request has been sent to the daemon by some client.

   :arg: The request as a dictionary (XXX)

.. daemonevt:: processing

   A request is now being processed.

   :arg: The request as a dictionary, see above.

.. daemonevt:: blocked

   One or more requests have been blocked from execution.

   :arg: A list of request numbers.

.. daemonevt:: status

   The status of the executing script changed.

   :arg: A tuple of (status constant, line number).  XXX constants

.. daemonevt:: watch

   Watch expressions have changed.

   :arg: A dictionary of watch expression names and their values.

.. daemonevt:: mode

   The session's mode has changed.

   :arg: The new mode (``master``, ``slave``, ``simulation`` or
      ``maintenance``).

.. daemonevt:: cache

   A new cache value has arrived.

   :arg: A tuple of (timestamp, key, operation, value).
      The value is the raw cache value, for NICOS related values this is a
      repr-stringified value.

.. daemonevt:: dataset

   A new data set has been created.

   :arg: The `nicos.core.data.Dataset` object.

.. daemonevt:: datapoint

   A new point has been added to the dataset.

   :arg: A tuple of (xvalues, yvalues).

.. daemonevt:: datacurve

   A new data curve has been added to the dataset.

   :arg: A tuple of (curve name, xvalues, yvalues).

.. daemonevt:: liveparams

   Set the data parameters for the next `livedata` event.

   :arg: A tuple of (tag, filename, dtype, nx, ny, nt, time), where

      - ``tag``: an application specific "tag" for the data format
      - ``filename``: (eventual) filename of the data being transferred
      - ``dtype``: data type of each pixel, in numpy format (such as ``<u4``)
      - ``nx``, ``ny``, ``nt``: array dimensions
      - ``time``: the counting time in seconds

.. daemonevt:: livedata

   New live data to display on the client.

   :arg: The data, as an *unserialized* byte string.

.. daemonevt:: simresult

   A simulation is finished.

   :arg: The result of the simulation as a tuple of (estimated minimum time in
       seconds, dictionary of devices and their moving range).

.. daemonevt:: showhelp

   The user requested help to be shown.

   :arg: A HTML string to be displayed.

.. daemonevt:: clientexec

   The user requested something to be executed on the client side.

   :arg: A tuple of (function name, arg1, ...).

.. daemonevt:: watchdog

   A watchdog warning has been emitted.

   :arg: A tuple of (event type, timestamp, data).

.. daemonevt:: debugging

   Debug mode has been toggled.

   :arg: True or False, whether debug is on or off.

.. daemonevt:: plugplay

   A plug-and-play event has occurred.

   :arg: A tuple of (event type, data, ...)

.. daemonevt:: setup

   New setups have been loaded in the session.

   :arg: A tuple of (all loaded setups, explicitly loaded setups).

.. daemonevt:: device

   Devices have been added/removed in the session.

   :arg: A tuple of (type, device names).
