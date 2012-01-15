.. _setups:

=========================
Configuring NICOS: Setups
=========================

-----------
Setup files
-----------

NICOS supports the concept of different instrument setups.  Not all devices that
can be used at an instrument will be present all the time, so they need not be
loaded.

A specific set of devices (and commands, which supports the notion of
specialized commands) is collected in a "setup file", a Python module in the
subdirectory ``setups`` of the site-specific NICOS root directory.

A setup file can consist of the following entries, all of which are optional:

``name``
   A string describing the setup in more detail than the module name.

``group``
   A string giving the group of the setup (meaning to be decided later).

   .. XXX "simulated" and "special" are already used

``includes``
   A list of names of setups that this one requires to be loaded.  Using this
   function, setups can be constructed very modularly, usually without
   duplicating the entry for any device.

``sysconfig``
   A dictionary with basic system configuration values.  See :ref:`sysconfig`
   below.  This is generally only put in one very basic setup file that is
   included from other, more high-level files.

``devices``
   A dictionary of devices, where the key is the device name and the value is a
   device definition, see :ref:`deviceentries` below.

``modules``
   A list of Python module names where additional user commands are loaded from.

``startupcode``
   A string of Python code that is executed after the setup file has been
   processed and the devices that are marked for automatic creation have been
   created.

``extended``
   A dictionary, reserved for future use.

.. XXX document "extended" more once we have use for it.


.. _deviceentries:

-------------------------------------
Entries in the ``devices`` dictionary
-------------------------------------

A device definition consists of a call like ``device(classname, parameters)``.
The class name is fully qualified (i.e., includes the package/module name).  See
the :doc:`class documentation <classes/index>` for the existing device classes.
The parameters are given as keyword arguments.  Here are some example
``devices`` entries::

   devices = dict(
       p   = device('nicos.taco.AnalogInput',
                     tacodevice = 'mira/ccr/pressure',
                     unit = 'bar'),

       mth_motor = device('nicos.taco.Motor',
                     tacodevice = 'mira/motor/mth',
                     lowlevel = True,
                     unit = 'deg'),

       mth_coder = device('nicos.taco.Coder',
                     tacodevice = 'mira/coder/mth',
                     lowlevel = True,
                     unit = 'deg'),

       mth = device('nicos.generic.Axis',
                   motor = 'mth_motor',
                   coder = 'mth_coder',
                   abslimits = (0, 100),
                   userlimits = (0, 50)),
   )

For example, an instrument with varying sample environment could have two setup
files, ``cryostat`` and ``oven``, where both include a ``base`` file that could
contain the monochromator, sample table and detector that always stay the same.

On startup, an empty setup is initialized by NICOS.  The user then loads a setup
using the ``NewSetup('modulename')`` command.  Each time the ``NewSetup``
command is used, the previous setup is unloaded and the created devices are
destroyed.  When more setups need to be loaded at the same time, the
``AddSetup('modulename')`` command can be used.


.. _sysconfig:

----------------------------
The ``sysconfig`` dictionary
----------------------------

The possible entries for the ``sysconfig`` dictionary are:

.. data:: cache

   A string giving the hostname of the cache server (or ``hostname:port``, if
   the cache runs on a port other than 14869).  If this is omitted, no caching
   will be available.

   See also :ref:`caching`.

.. data:: instrument

   The name of the instrument device, defined somewhere in a ``devices``
   dictionary.  The class for this device must be
   :class:`nicos.instrument.Instrument` or an instrument-specific subclass.

   See :ref:`principles`.

.. data:: experiment

   The name of the experiment "device", defined somewhere in a ``devices``
   dictionary.  The class for this device must be
   :class:`nicos.experiment.Experiment` or an instrument-specific subclass.

   See :ref:`principles`.

.. data:: datasinks

   A list of names of "data sinks", i.e. special devices that process measured
   data.  These devices must be defined somewhere in a ``devices`` dictionary
   and be of class :class:`nicos.data.DataSink` or a subclass.

   See also :ref:`datahandling`.

.. data:: notifiers

   A list of names of "notifiers", i.e. special devices that can notify the user
   or instrument responsibles via various channels (e.g. email).  These devices
   must be defined somewhere in a ``devices`` dictionary and be of class
   :class:`nicos.notify.Notifier` or a subclass.

   See also :ref:`advanced`.
