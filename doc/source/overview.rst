Overview
========

As with many other control systems, NICOS presents the hardware to the user as
*devices*.  Devices can be very limited in scope and control a single bit
input/output, or very complicated and move a whole triple-axis instrument in
Q-omega space.  The devices in a session form a hierarchy: more high-level
devices can depend on more low-level devices, which are *attached* to each
other.

Most devices fall into three basic classes: readable, moveable and measurable
devices.  Basic functionality of hardware devices such as "read the value" and
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

The components of the NICOS system are described in more detail on
:ref:`the following page <components>`.
