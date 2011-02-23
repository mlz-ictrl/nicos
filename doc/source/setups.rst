============
NICOS setups
============

-----------
Setup files
-----------

NICOS supports the concept of different instrument setups.  Not all devices that
can be used at an instrument will be present all the time, so they need not be
loaded.

A specific set of devices (and commands, which supports the notion of
specialized commands) is collected in a "setup file", a Python module in the
subdirectory ``setup`` of the NICOS root directory.

A setup file consists of the following entries:

``name``
   A string describing the setup in more detail than the module name.

``group``
   A string giving the group of the setup (meaning to be decided later).

``includes``
   A list of names of setups that this one requires to be loaded.  Using this
   function, setups can be constructed very modularly, usually without
   duplicating the entry for any device.

``devices``
   A dictionary of devices, where the key is the device name and the value is a
   device definition, see below.

``modules``
   A list of Python module names where additional user commands are loaded from.

``startupcode``
   A string of Python code that is executed after the setup file has been
   processed and the devices that are marked for automatic creation have been
   created.

A device definition consists of a call like ``device(classname, parameters)``.
The class name is fully qualified (i.e., includes the package/module name).  The
parameters are given as keyword arguments.  An example ``devices`` entry is::

   devices = dict(
       m1 = device('virtual.VirtualMotor',
                   autocreate = False,
                   initval = 1,
                   unit = 'deg'),

       m2 = device('virtual.VirtualMotor',
                   autocreate = False,
                   initval = 0.5,
                   unit = 'deg'),

       a1 = device('axis.Axis',
                   adev = {'motor': 'm1', 'coder': 'c1', 'obs': []},
                   absMin = 0,
                   absMax = 100,
                   userMin = 0,
                   userMax = 50),
   )

For example, an instrument with varying sample environment could have two setup
files, ``cryostat`` and ``oven``, where both include a ``base`` file that could
contain the monochromator, sample table and detector that always stay the same.

On startup, an empty setup is initialized by NICOS.  The user then loads a setup
using the ``NewSetup('modulename')`` command.  Each time the ``NewSetup``
command is used, the previous setup is unloaded and the created devices are
destroyed.  When two setups really need to be loaded at the same time, the
``AddSetup('modulename')`` command can be used.
