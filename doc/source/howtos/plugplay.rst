Creating a plug'n'play environment
==================================

NICOS allows treating external hardware as **plug'n'play** components.  This
HOWTO explains how to set up this behavior.


Mechanism
---------

Plug'n'play components need to register themselves in the cache in order to be
discovered by NICOS.  The relevant cache entry is ::

    se/<identifier>/nicos/setupname='<setup>'

where ``<identifier>`` is a unique identifier of the plug'n'play component, and
``<setup>`` is the name of the NICOS setup that should be loaded to control the
component from a NICOS daemon.  The setup in question must have its group set to
``'plugplay'``.

When a key of this form is set in the cache, and the specified setup exists in
the current setup paths, the daemon will emit an event to all clients and they
can display a notification, allowing users to load the corresponding setup.

When the key is unset, or expires, the daemon will emit another event that in
turn allows users to unload the now-unneeded setup.  For this to work reliably,
the plug'n'play component should send the key with a time-to-live, and refresh
it periodically while it is still running, so that disconnects are detected even
when the component is not shut down properly.


Implementation with ``cachereg``
--------------------------------

At MLZ, a script named ``cachereg`` [#f1]_ is currently used to implement the
plug'n'play mechanism for sample environment and other "optional" boxes at
instruments.

The ``cachereg`` process is started when the box boots up and sends a UDP
broadcast to find all cache processes in its network.  All running cache servers
in that network will get a periodic update on the ``se/...`` key described above
that this box is available.

The convention used by ``cachereg`` is that the ``<identifier>`` is always the
fully-qualified hostname, while the ``<setup>`` name is always the short
hostname (first component of the DNS name) of the machine it is running on.


.. rubric:: Footnotes

.. [#f1] ``cachereg`` is available from
   https://forge.frm2.tum.de/cgit/cgit.cgi/frm2/general/boxtools.git/tree/cachereg
