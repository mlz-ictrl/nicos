Overview
========

NICOS is a control system with several components:

* Execution daemon

  The execution daemon (in short daemon) is designed to excute the user scripts
  to control the instrument from the point of the user/scientist.

  It runs in the background and interacts with the user interfaces, graphical or
  command line, via a distinct protocol.  It does not depend on having a user
  interface connected, however, so that measurement time is not lost if the
  interface running on the user-facing machine dies.  After reconnecting to the
  server the user may see all results, messages, ... from the time when the
  client was disconnected.

* Graphical user interface

  There exists a graphical user interface whose layout may configured
  individually for each instrument.  There are some standard components for the
  GUI but it also possible to add custom elements (widgets or panels) for the
  GUI.

* Command line interface

  There is also a pure command line interface to control the instrument via
  execution daemon.  Since in the graphical user interface also a command line
  element exists, it is mainly useful for low-bandwidth connections.

* Electronic logbook

  For scientists performing an experiment at one of the instruments it is
  necessary to remember what they have done.  To support them in this, their
  actions in NICOS will be logged in a human-readable form.  This is the job of
  the 'Electronic logbook', which stores the data as HTML files which can be
  viewed by any HTML browser; the resulting documentation can be taken home by
  the user to get a documentation of their experiment.

* Data cache

  The data cache was designed to reduce access to the hardware.  Since some
  hardware components communicate very slowly via their communication interfaces
  the whole system could become 'lethargic'.  With the help of the cache, such
  hardware access will be reduced by storing device information (such as
  positions, voltages, etc) for a certain amount of time.  All information of
  the devices inside the system will be taken from the cache.

  The cache is also used as an archiving system for the instrument status.
  Since every bit of information about devices is present and archived with a
  timestamp, users will be able to query information about the parts of the
  instrument during the time of their experiment.  This will help to find out if
  there were some problems or the experimenters have some questions about the
  state of a component during their measurement time.

  It works close together with the 'Poller'.

* Poller

  The poller component periodically queries volatile information such as current
  sensor readings from the devices inside the instrument, sample environments,
  etc. and pushes these data into the data cache.

* Watchdog

  For some good reasons some of the parameters during the experiment should not
  leave their limits.  This could be done manually by watching their values
  during the experiment, but this not very convenient for a long running
  experiment.

  The watchdog takes this job.  It checks configured parameters for their limits
  and informs the user about problems.  This can be done by pop-ups in the user
  interface, sending an email, sending a text message etc.

* Status Monitor

  Some of the instrument resposible are used to look at there instrument parameters
  to find out the current state of the instrument.  In former time the looked at
  their electronic racks, but in nower time the classical racks are more or less
  gone.  To fill this gap a status monitor was developped, which is highly
  configurable according to the requirements of the instrument.
