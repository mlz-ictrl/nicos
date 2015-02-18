.. _components:

Components of the NICOS system
==============================


.. digraph:: Components

    rankdir = LR;

    subgraph cluster0 {
        node [style=filled,color=white];
        style = "rounded,filled";
        color = lightsalmon;


        "nicos-watchdog" {rank = same; "nicos-elog"; "nicos-poller";
                          "nicos-collector"; "nicos-watchdog"}
        "nicos-cache" {rank = same; "nicos-daemon";}

        "nicos-cache"   -> "nicos-daemon"
        "nicos-cache"   -> "nicos-poller"
        "nicos-cache"   -> "nicos-watchdog"
        "nicos-cache"   -> "nicos-elog"
        "nicos-cache"   -> "nicos-collector"
        "nicos-watchdog"-> "nicos-cache"
        "nicos-daemon"  -> "nicos-cache"
        "nicos-poller"  -> "nicos-cache"
        "nicos-collector" -> "nicos-cache"

        edge[style=invis];
        "nicos-watchdog" -> "nicos-poller" -> "nicos-elog"

        label = "Servers";
    }

    subgraph cluster1 {
        node [style=filled,color=white];
        style = "rounded,filled";
        color = lightblue;

        "nicos-gui"{rank = same; "nicos-history";}
        "nicos-history"
        "nicos-monitor"
        "nicos-client"

        edge[style=invis];
        "nicos-gui" -> "nicos-history" -> "nicos-monitor" -> "nicos-client"

        label = "Clients";
    }


    "nicos-cache"   -> "nicos-gui"
    "nicos-cache"   -> "nicos-client"
    "nicos-cache"   -> "nicos-monitor"
    "nicos-cache"   -> "nicos-history"
    "nicos-daemon"  -> "nicos-gui"
    "nicos-daemon"  -> "nicos-client"
    "nicos-gui"     -> "nicos-daemon"
    "nicos-client"  -> "nicos-daemon"


The NICOS components come in the form of executables located in the ``bin``
subdirectory of the NICOS source:


.. index:: nicos-aio, nicos-gui, nicos-client

Shells
------

These components allow the user -- in some form or other -- to interact with the
NICOS system and execute commands.

.. describe:: nicos-gui

   This is the GUI client part of the server-client execution shell and the main
   user-facing process.  It connects to a ``nicos-daemon`` instance (see below)
   that controls the instrument.  The GUI uses `Qt <https://qt.io>`_ for the
   basic functionality, and `GR <https://gr-framework.org/>`_ for the data
   plotting and analysis windows.

   The GUI's layout can be configured individually for each instrument.  There
   are some standard components for the GUI, but it is possible to add custom
   elements (widgets, panels and commandlets).

.. describe:: nicos-client

   This is a pure text-based interface to control the instrument via execution
   daemon.  Since the graphical user interface also contains a command line
   element, it is mainly useful for low-bandwidth connections.

.. describe:: nicos-aio

   This is the most basic NICOS shell.  ``nicos-aio`` (short for "all-in-one")
   takes the job of script execution and user interface, and presents to the
   user a slightly enhanced builtin Python shell, where commands can be
   executed.

   ``nicos-aio`` is not expected to be used in normal experiments.


.. index:: nicos-monitor, nicos-history

Other clients
-------------

These programs are clients that don't provide shell functionality.

.. describe:: nicos-monitor

   The status monitor is a display-only interface that can replace looking at
   electronics racks to quickly determine the state of the instrument.  It can
   display any information available to NICOS -- such as values of hardware
   devices or experiment information -- in the form of text, plots, or a
   graphical representation of the instrument, or parts thereof.

   The monitor can be run as a graphical application, or as a background task
   that generates an HTML page for remote viewing.

   See :ref:`monitor`.

.. describe:: nicos-history

   This GUI program plots values (e.g. temperatures) from the cache over time.
   It is the standalone version of a panel normally available in ``nicos-gui``.

   See :ref:`history`.


.. index:: nicos-cache, nicos-daemon, nicos-poller, nicos-elog, nicos-watchdog

Daemons
-------

These programs provide services and are designed to run as daemons once per
instrument.

.. describe:: nicos-cache

   The NICOS data cache was designed to keep a record of the system state, and
   reduce access to the hardware.  Since retrieval of some hardware state is
   slow, updating those only occasionally, and caching them, is required.  The
   cache takes this job and records a time-to-live for each stored value.  When
   information about devices is needed by NICOS, it can be taken from the cache.

   The cache also serves as an archival system for the instrument status.  Since
   every bit of information about devices is present and archived with a
   timestamp, users will be able to query information about the parts of the
   instrument during the time of their experiment.  In very simple situations,
   the NICOS daemon can also run without the cache component, but services like
   the watchdog or status monitor will not work without it.

   See :ref:`cache`.

.. describe:: nicos-daemon

   The execution daemon (in short daemon) is designed to excute the user scripts
   to control the instrument from the point of the user/scientist.

   It runs in the background and interacts with the user interfaces, graphical
   or command line.  It does not depend on having a user interface connected,
   however, so that measurements continue when an interface running on a
   user-facing machine dies.  After reconnecting to the daemon, users can catch
   up on all new messages and measurement results since the client was
   disconnected.

   See :ref:`daemon`.

.. describe:: nicos-poller

   The poller periodically queries volatile information such as current sensor
   readings from all devices in the instrument setup and additional setups like
   sample environments, and pushes updates to the NICOS cache.

   See :ref:`poller`.

.. describe:: nicos-elog

   This daemon provides the "electronic logbook", which tries to support
   scientists in documenting and recollecting the course of an experiment.  It
   collects information about special events such as "new sample" or "scan
   finished", and writes them to disk in HTML form, which can serve as an
   electronic logbook of the experiment that is easier to read than a mere
   plain-text logfile.  This logbook is typically taken home together with the
   data files.

   See :ref:`elog`.

.. describe:: nicos-watchdog

   The watchdog is a flexible alarm system that checks updates to values in the
   cache for user-defined conditions and sends out notifications when they are
   hit.  Use cases include notification about required user intervention
   (e.g. filling of cryogen), early diagnosis of pending failures, or deviation
   from required limits of some devices.

   Notifications can be configured to pop up in the user interface, send an
   email, a text message etc.  NICOS code can also be run to stop counting
   or begin a "rescue" sequence.

   See :ref:`watchdog`.

.. describe:: nicos-collector

   This daemon provides the possibility to forward cache events from one cache
   instance to another one.

   See :ref:`collector`.
