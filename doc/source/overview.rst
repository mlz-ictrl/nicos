Overview
========

As with many other control systems, NICOS presents the hardware to the user as
*devices*.  Devices can be very limited in scope and control a single bit
input/output, or very complicated and move a whole triple-axis instrument in
Q-omega space.  The devices in a session form a hierarchy: more high-level
devices can depend on more low-level devices, which are *attached* to each
other.

Most of these devices fall into a few basic classes:

* :class:`Readable <nicos.core.device.Readable>`: A device which periodically
  reads a value from somewhere (e.g. a temperature sensor).

* :class:`Waitable <nicos.core.device.Waitable>`: A :class:`Readable
  <nicos.core.device.Readable>` which can execute some action and wait for its
  completion.  It is usually used as a "controller" device for other devices,
  for example multiple motors which move together.  The controller device can
  initiate the combined movement via a custom command and then be waited upon
  until all "attached" devices have completed their individual movements.

* :class:`Moveable <nicos.core.device.Moveable>`: A :class:`Waitable
  <nicos.core.device.Waitable>` which can start a "movement" in order to change
  a particular value.  A typical example would be a motor or a temperature
  controller.

* :class:`Measurable <nicos.core.device.Measurable>`: A :class:`Waitable
  <nicos.core.device.Waitable>` for acquiring data.  The data acquisition is
  "started" via the :func:`count <nicos.commands.measure.count>` or by one of
  the :ref:`scan commands <scanning_commands>`.  A typical example would be a
  detector.

These core devices are located in :mod:`nicos.core.device`. See their respective
documentation for more.

Basic functionality of hardware devices such as "read the value" and
"read the status", or "move to a new value" and "reset" is contained in these
three classes.

The basic interface for setting up an instrument is to configure a number of
devices with properties called *parameters*.  Since this interface should apply
to the whole system, NICOS extends the meaning of "device" and also provides
global services as devices.  An example would be the *experiment* device, which
allows configuring settings relevant to a whole experiment with the same
device-parameter interface.  These "special" devices don't usually inherit the
basic readable/moveable classes.

Collections of devices are configured in *setup* files.  Every setup can be
loaded into a session as a unit with all its configured devices, and, like
devices, depend on other setups to be loaded.

Since the object model in Python is quite flexible, devices are mapped directly
to instances of a device class.  The context in which these device instances are
created and managed is called a *session*.  An important design principle of
NICOS is that there can be multiple sessions running, each in its own process,
with the same devices instantiated.  To synchronize write access to the devices,
a session has a *mode*, the most important modes being "master" and "slave".  As
the name suggests, there may only be one master session.

The device-parameter system is complemented by a process called *cache*.  The
cache provides a key-value store that keeps the state of the system in an
in-memory database, keeping track of a time-to-live for each key, but also has
the option of storing the history of each value, with different supported
backends.

The usual mode of operation is that the master session is the so called
*execution daemon*, which executes user measurement scripts and exports a
network interface for clients.  These clients are available in graphical and
command-line variants.

In parallel, there is usually a process called *poller* that starts a session
for each setup and queries its devices periodically for value and status.  These
state updates are forwarded to other NICOS sessions via the cache.

The components of the NICOS system are described in more detail
:ref:`on this page <components>`.
