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

A "request" frame on the command connection begins with the ASCII byte ENQ
(0x5), followed by a 2-byte "command code", and the length of the payload as a
network-order (big-endian) unsigned 32-bit integer.  The payload must be a
serialized Python tuple with the arguments for the command.

A reply frame on the command connection has one of three types: "ok", "error" or
"data".  The first byte selects the type with the ASCII values ACK (0x6), NAK
(0x15) and STX (0x2) respectively.

"ok" frames have no further content; they consist of only one byte.

For "error" and "data" frames, the following four bytes encode the length of the
payload (i.e. frame length excluding first byte and length) as a network-order
unsigned 32-bit integer.

In both cases, the payload is a serialized Python object -- for "error" frames
it should deserialize to a simple string explaining the error.

For "data" frames sent from the daemon to the client, the payload is a
serialized Python object.

**Event connection**

On this connection, all data flows from daemon to client.  "Event" frames
consist of an STX byte, a 2-byte "event code", a payload length encoded as
usual, and the payload being the event data.

For most events, the data is a serialized Python object, except for those where
a lot of raw data has to be transferred, such that serialization is both slow
and unnecessary.  In the Events_ documentation, deserialized transfer of data is
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

The daemon then expects a "authenticate" command with a serialized dictionary,
giving the login name (key "login"), the password (possibly hashed) (key
"passwd") and a string to use as the :envvar:`DISPLAY` environment variable on
the server (key "display").  The latter is mostly obsolete, as it is
incompatible with logins from multiple machines; no value needs to be
transferred.

If the login name and password are accepted, the daemon sends back an "ok" frame
and connection is ready to accept further commands.

At this time, the client can open a second connection to the server port and
send the client ID.  This connection will be detected as the event connection,
and the client can then start receiving event frames on this connection.


Daemon functionality
====================

The daemon operates with several threads: one thread accepts new connections.
Two threads are started per connection: one to receive and handle commands, and
one to send new events (which are pushed to the thread via a Queue).  Another
thread executes user scripts, and a last thread monitors "watch expressions"
that can be set by the clients and are evaluated continuously during runtime.

Execution of code in the "script thread" is subject to a Python trace function,
which means that debugger-like functionality is available: scripts can be
paused, stopped and updated at runtime.


.. _daemon-commands:

Commands
========

These commands can be sent over the command socket.

Script commands
---------------

.. daemoncmd:: queue
.. daemoncmd:: start
.. daemoncmd:: unqueue
.. daemoncmd:: update
.. daemoncmd:: rearrange

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
.. daemoncmd:: eventunmask
.. daemoncmd:: getversion
.. daemoncmd:: transfer
.. daemoncmd:: keepalive

Experimental commands
---------------------

.. daemoncmd:: debug
.. daemoncmd:: debuginput

Terminating a connection
------------------------

.. daemoncmd:: unlock
.. daemoncmd:: quit


.. _daemon-events:

Events
======

These are the events emitted by the daemon and transferred on the event
connection.  Event data is serialized (using pickle, see Serialization_).
However, some events can also transport a number of blobs in addition
to the serialized data.

The possible events are listed in the `nicos.protocols.daemon.DAEMON_EVENTS`
dictionary, which maps the event name to a numeric identifier used in some
protocols.

.. daemonevt:: message

   A new log message has been emitted.

   :arg: The new message, as a list with the following members:

      - source logger name
      - message time as Unix timestamp
      - message level as a number
      - message text
      - exception traceback if present
      - message prefix (normally empty, but can be selected different for
        dry-run output, see `simulate`)

.. daemonevt:: request

   A new request has been sent to the daemon by some client.  Requests are
   generated either by new scripts to execute (via `queue`) or by calling
   emergency stop while no script is running.

   This event means that the request has been queued, but is not yet being
   executed (see `processed` below).

   Each request has a request ID, which is used to identify the request in
   subsequent commands (e.g. to cancel the request) or events.

   :arg: The request as a dictionary.  The dictionary contents depend on the
      request type:

      - all requests have ``'reqid'`` (request ID) and ``'user'`` (user name
        who originated the request) keys
      - script requests also have ``'name''`` (script name/filename) and
        ``'script'`` (code to execute) keys

.. daemonevt:: processing

   A request is now being processed.

   :arg: The request as a dictionary, as for ``request``.

.. daemonevt:: done

   A request is done processing.

   :arg: The request as a dictionary, as for ``request``, but with an additional
      key:

      - ``'success'`` - a boolean, true if the request executed without an
        exception (or emergency stop) raised

.. daemonevt:: updated

   A queued request has been updated.

   :arg: The request as a dictionary, see above.

.. daemonevt:: blocked

   One or more requests have been blocked from execution.

   :arg: A list of request IDs.

.. daemonevt:: rearranged

   The request queue has been rearranged.

   :arg: A list of request IDs that gives the new ordering.

.. daemonevt:: status

   The status of the executing script changed.

   :arg: A tuple of (status constant, line number).  Status constants are
      defined in `nicos.protocols.daemon`:

      - ``STATUS_IDLE`` -- nothing is running
      - ``STATUS_IDLEEXC`` -- nothing is running, and last script raised an
        unhandled exception
      - ``STATUS_RUNNING`` -- a script is running
      - ``STATUS_INBREAK`` -- execution is currently paused
      - ``STATUS_STOPPING`` -- execution is stopping (the `ControlStop`
        exception has been raised, but not yet propagated to toplevel)

.. daemonevt:: watch

   Watch expressions have changed.

   :arg: A dictionary of watch expression names and their values.

.. daemonevt:: mode

   The session's mode has changed.

   :arg: The new mode (``'master'``, ``'slave'``, ``'simulation'`` or
      ``'maintenance'``).

.. daemonevt:: cache

   A new cache value has arrived.

   :arg: A tuple of ``(timestamp, key, operation, value)``.
      The value is the raw cache value, for NICOS related values this is a
      repr-stringified value.

      Key expiration and active deletion are signified by either by
      ``operation`` being `~nicos.protocols.cache.OP_TELLOLD` or ``value`` being
      an empty string, respectively (for the ``OP_`` constants see the
      `nicos.protocols.cache` module).

.. daemonevt:: dataset

   A new data set has been created.

   :arg: The `nicos.core.data.BaseDataset` object.

.. daemonevt:: datapoint

   A new point has been added to the dataset.

   :arg: A tuple: ``(dataset uid, xvalues list, yvalues list)``.

.. daemonevt:: datacurve

   A new fit data curve has been added to the dataset.

   :arg: A tuple of ``(curve name, xvalues list, yvalues list)``.

.. daemonevt:: livedata

   An assortment of live data.

   :arg: ``liveparams`` and some ``datablobs``

   ``liveparams``:
   Describes the incoming data as a dictionary with the following keys:

      - `uid`: uuid of the dataset
      - `time`: runtime in sec
      - `det`: detector name
      - `tag`: 'live' or 'file'
      - `filedescs`: list of dictionaries with the following keys (for 'file')

         - `filename`: filename to read from
         - `fileformat`: format of the specified file

      - `datadescs`: list of dictionaries with the following keys (for 'live')

         - `filename`: filename for caching
         - `dtype`: numpy data type for the data values
         - `shape`: shape of one dataset
         - `labels`: dictionary describing how to label the axis:

            - allowed keys: `x`, `y`
            - allowed values: dict with the following keys:

              - `title`: axis title
              - `define`: allowed values:

                - `classic`: use range(shapesize) for the labels
                - `range`: equidistant distribution from first to last (defined
                  by ``start + step * number_of_steps``), additional keys:

                  - `start`: start value
                  - `step`: step size
                  - `length`: number of steps
                - `array`: custom labels array (typically not equidistant),
                  additional keys:

                  - `index`: index in the labels array (default=0)
                  - `dtype`: data type of the label values
         - `plotcount`: amount of datasets contained in the associated
           data buffer

   in short:

      .. code-block:: python

          dict(
              uid=str,
              time=float,
              det=str,
              tag=oneof('live','file'),
              # mandatory if tag == 'file', else optional
              filedescs=[dict(
                  filename=str,
                  fileformat=str,
              ),]
              # mandatory if tag == 'live', else optional
              datadescs=[dict(
                  dtype=str,
                  shape=oneof((x,), (y, x), (t, y, x), ... ),
                  labels={
                      'x': dict('define': oneof('classic', 'range', 'array')),
                      ['y': dict('define': oneof('classic', 'range', 'array'))],
                  plotcount=int,
              ),]
          )

   ``datablobs``: a list of data buffers. Each entry belongs to one of two
   categories:

      - `livedata`: the actual data
      - `livelabels`: labels for the axis one buffer per dataset

   The first entries in datablobs will be processed as `livedata`.  The
   `livedata` buffer is a list of `plotcount` (in the associated `datadesc`)
   datasets.

   The last data blobs will be processed as `livelabels`.  The maximum amount
   of ``livelabels`` is the length of the ``labels`` in the ``datadescs``
   entry.  These buffers will be used only in case that the `labels` have a
   `define` of 'array'. In this case the `index` entry of the `labels` entry
   points to the corresponding entry in `livelabels`.

.. daemonevt:: simresult

   A dry run/simulation is finished.

   :arg: The result of the dry run as a tuple of (estimated minimum time in
       seconds, dictionary of devices and their moving range).

       If an exception occurred during simulation, the minimum time returned
       is -1.

.. daemonevt:: showhelp

   The user requested help to be shown.

   :arg: A HTML string to be displayed.

.. daemonevt:: clientexec

   The user requested something to be executed on the client side.  This is
   generally a NICOS library function that opens a GUI window, which cannot be
   done on the server side.

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

.. daemonevt:: experiment

   The current experiment has been changed.

   :arg: The new proposal string.

.. daemonevt:: prompt

   The script has been paused, and the user should be prompted to
   confirm continuation.

   :arg: A two-element tuple (prompt text, prompt uid) for simple confirmations,
       or (prompt text, prompt uid, validator object, preset value) for value
       inputs.

.. daemonevt:: promptdone

   A prompt sent with `prompt` has been responded to by a user,
   cancel any prompts.

   :arg: A single-element tuple (prompt uid,)
