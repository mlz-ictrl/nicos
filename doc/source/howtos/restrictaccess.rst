Limiting access to devices
--------------------------

For some applications, or at some installations, it is required to limit access
to devices.  For example, normal users may read devices and their parameters,
but should not move any of them to avoid wrecking of parts of the instrument.
This can be achieved in a few different ways, statically or dynamically.


Limitation basics
^^^^^^^^^^^^^^^^^

NICOS can require conditions to use specific functionality.  This is based on
key-value properties, which can be used in different places described below.
The following keys and values are currently defined:

mode
   Requires a session execution mode (one of 'master', 'slave', 'simulation',
   'maintenance').  For use in modules, constants for these values (e.g.
   MASTER) are defined in `nicos.core.constants`.

level
   Requires at least a certain user level for the daemon connection (one of
   'guest', 'user', 'admin').  One of these user levels is assigned to every
   account that may connect.  Constants are also defined for these values.


Static limitation of methods via the `requires` decorator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If some functionality of a device class is always to be restricted, you can
achieve this limitation by using :func:`~nicos.core.device.requires` as a
decorator on the method.  It receives keyword arguments as described above.
For example::

   from nicos.core import requires, ADMIN

   @requires(level=ADMIN)
   def calibrate(self):
       """Do some potentially dangerous work."""


Setup-based limitation via the `requires` device parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the device is always allowed to move only from a restricted set of persons,
then the device can be configured with the
:attr:`~nicos.core.device.Moveable.requires` parameter.

It takes the same keys/values as described above, so if you want to allow write
access only to people with 'admin' level, you can use
``requires = {'level': 'admin'}``.

Please have in mind the 'admin' is a user level, not the user name.  Several
users may have the role 'admin'.


Dynamic limitation via the 'fix' command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If write access to a device should be limited only temporarily, the use of
the :func:`~nicos.commands.device.fix` command is recommended.

A user may use this command to forbid write access for everyone, with a given
reason.

The restriction may removed by users with at least the same user level as the
initial user, using the :func:`~nicos.commands.device.release` command.
