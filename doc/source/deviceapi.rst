====================
Device API reference
====================

.. module:: nicos.core.device

----------------
Device interface
----------------

NICOS models every device type as a Python class, and concrete devices as
instances of these classes.  There are also abstract classes that do not map to
real devices, but serve to define the interface for derived classes.

For almost any action on a device, there are two methods:

* The public method, e.g. ``device.start()`` is what the user or a user command
  will call.  It typically is only present on the most abstract class that has
  that method and delegates most of the work to the implementation method,
  except for repetitive tasks that always have to be executed for that action.
* The implementation method, prefixed with ``do``, e.g. ``device.doStart()``
  executes the action for the specific device.  It is overwritten in specific
  subclasses.

When writing a device class for a specific device, only those implementation
methods need to written that the device can support; the others will be skipped
when called by the public methods.

Additional public methods can be implemented for specific devices, such as
``setPosition()`` for motors; the ``method``/``doMethod`` split should only be
applied if the ``method`` implementation does something common for all possible
implementations of ``doMethod``.  Public methods that can be called by the user
should be decorated with `.usermethod`.

--------------
Device classes
--------------

The base classes for all devices are contained in the module
:mod:`nicos.core.device` and re-exported in :mod:`nicos.core`.  There is a
hierarchy of classes that correspond to varying levels of interaction that is
possible with the device:

``Device``
==========

.. class:: Device

   This class is the most basic class to use for NICOS devices.  It supports
   setting parameters from the configuration, and allows the user to get and set
   parameter values via automatically created properties.

   .. rubric:: Special attributes

   .. attribute:: parameters

      Device objects must have a :attr:`parameters` class attribute that defines
      the available additional parameters.  It must be a dictionary mapping
      parameter name to a :class:`~nicos.core.params.Param` object that
      describes the parameter's properties (e.g. whether is it user-settable).

      The :attr:`parameters` attribute does *not* need to contain the parameters
      of base classes again, they are automatically merged.

      As an example, here is the parameter specification of the ``Device`` class
      itself::

          parameters = {
              'description': Param('A description of the device', type=str,
                                   settable=True),
              'lowlevel':    Param('Whether the device is not interesting to users',
                                   type=bool, default=False),
              'loglevel':    Param('The logging level of the device', type=str,
                                   default='info', settable=True),
          }

   .. attribute:: parameter_overrides

      While a subclass automatically inherits all parameters defined by base
      classes, it can make changes to parameters' properties using the override
      mechanism.  This dictionary, if present, must be a mapping of existing
      parameter names from base classes to :class:`~nicos.core.params.Override`
      objects that describe the desired changes to the parameter info.

      For example, while usually the :attr:`~Readable.unit` parameter is
      mandatory, it can be omitted for devices that can find out their unit
      automatically.  This would be done like this::

         parameter_overrides = {
             'unit': Override(mandatory=False),
         }

   .. attribute:: attached_devices

      Device classes can also have an :attr:`attached_devices` attribute that
      defines the class's "attached devices" it needs to operate, such as a
      low-level communication device, or motor and encoders for an axis class.
      It maps the "internal name" (the device will be available as an attribute
      with that name) to the type of the device (which usually is an abstract
      type), and a string describing the purpose of the device.  For example::

         attached_devices = {
             'motor': (nicos.abstract.Motor, 'The motor to move'),
             'coder': (nicos.abstract.Coder, 'The coder for reading position'),
         }

      The actual attached devices for a specific instance (given in the
      instance's configuration) are then type-checked against these types.  As a
      special case, if the type is a list containing one type, such as
      ``[Readable]``, the corresponding entry in the configuration must be a
      list of zero to many instances of that type.

      The :attr:`attached_devices` attribute does *not* need to contain the
      entries of base classes again, they are automatically merged.

   .. rubric:: Public methods

   These methods are present on every Device.  They do not need to be
   reimplemented in custom devices.  Custom behavior is implemented in the
   various ``do...()`` methods described below.

   .. automethod:: init

   .. automethod:: shutdown

   .. automethod:: info

   .. automethod:: version

   .. method:: getPar(name)
               setPar(name, value)

      These are compatibility methods from the old NICOS system.  Parameter
      access is now done via a property for every parameter.

   .. rubric:: Parameter access

   For every parameter of a device class, a Python property is created on the
   object.  This means that every parameter can be read as ``dev.param`` and
   written as ``dev.param = value``.  Setting the parameter at runtime is
   disallowed if the ``settable`` parameter property is false.

   For every parameter, a read-related method can be defined (where "foo" is the
   parameter name):

   .. method:: doReadFoo()

      For every parameter "foo", a ``doReadFoo()`` method can be implemented.
      It will be called when the current parameter value is unknown, and cannot
      be determined from the cache.  It should read the parameter value from an
      independent source, such as the hardware or the filesystem.  If no such
      method exists, the parameter value will be the default value from the
      ``default`` parameter property, or if that is missing as well, a default
      value based on the type of the parameter (for number-like parameters, this
      is 0, for string-like parameters the empty string, etc).

   For every parameter, two write-related methods can be defined (where "foo" is
   the parameter name):

   .. method:: doWriteFoo(value)

      The ``doWriteFoo(value)`` method is called when the parameter is set by
      the user (or the program) in the current session, using ``dev.foo =
      value``.  This should write the new parameter value to the hardware, or
      write new parameter values of any dependent devices.  It is only called
      when the current session is in master mode.

      *value* is already type-checked against the parameter type.

      This method can raise :exc:`.ConfigurationError` if the new parameter
      value is invalid.

      If this method returns something other than ``None``, it is used as the
      new parameter value instead of the value given by the user.

   .. method:: doUpdateFoo(value)

      The ``doUpdateFoo(value)`` method, in contrast, is called *in every
      session* when the parameter is changed by the master session, and the
      parameter update is communicated to all other sessions via the cache.
      This method should update *internal* state of the object that depends on
      the values of certain parameters.  It may not access the hardware, set
      other parameters or do write operations on the filesystem.

      ``doUpdateFoo`` is also called when an instance is created and its
      parameters are initialized.

      This method can raise :exc:`.ConfigurationError` if the new parameter
      value is invalid.

   NB: The method names need to contain the parameter name with the first letter
   capitalized.

   .. rubric:: Parameters

   .. parameter:: name : string, optional

      The device name.  This parameter should not be set in the configuration, it
      is set to the chosen device name automatically.

   .. parameter:: description : string, optional

      A more verbose device description.  If not given, this parameter is set to be
      the same as the ``name`` parameter.

   .. parameter:: lowlevel : bool, optional

      Indicates whether the device is "low-level" and should neither be
      presented to users, nor created automatically.  Default is false.

   .. parameter:: loglevel : string, optional

      The loglevel for output from the device.  This must be set to one of the
      loglevel constants.  Default is ``info``.

   .. rubric:: Protected members

   These protected members are of interest when implementing device classes:

   .. attribute:: _mode

      The current :dfn:`execution mode`.  One of ``'master'``, ``'slave'``,
      ``'maintenance'`` and ``'simulation'``.

   .. attribute:: _cache

      The cache client to use for the device (see :class:`.CacheClient`), or
      ``None`` if no cache is available.

   .. attribute:: _adevs

      A dictionary mapping attached device names (as given by the
      :attr:`attached_devices` dictionary) to the actual device instances.

   .. attribute:: _params

      Cached dictionary of parameter values.  Do not use this, rather access the
      parameters via their properties (``self.parametername``).

   .. automethod:: _setROParam

   .. automethod:: _cachelock_acquire
   .. automethod:: _cachelock_release



``Readable``
============

.. class:: Readable

   This class inherits from :class:`Device` and additionally supports this
   public interface and implementation methods:

   .. automethod:: read

   .. automethod:: status

   .. automethod:: reset

   .. automethod:: poll

   .. automethod:: format

   .. automethod:: valueInfo

   .. method:: info()

      The default implementation of :meth:`Device.info` for Readables adds the
      device main value and status.

   .. automethod:: history

   .. rubric:: Parameters

   .. parameter:: fmtstr : string, optional

      A string format template that determines how :meth:`format` formats the
      device value.  The default is ``'%s'``.

   .. parameter:: unit : string, mandatory

      The unit of the device value.

   .. parameter:: maxage : float, optional

      The maximum age of cached values from this device, in seconds.  Default is
      5 seconds.

   .. parameter:: pollinterval : float, optional

      The interval for polling this device from the :dfn:`NICOS poller`.
      Default is 6 seconds.


``Moveable``
============

.. class:: Moveable

   This class inherits from :class:`Readable` and is the base class for all
   devices that can be moved to different positions (continuously or
   discretely).

   .. automethod:: start

   .. attribute:: valuetype

      This attribute gives the type of the device value, as in the ``type``
      parameter property.  It is used for checking values in :meth:`start`.

   .. automethod:: isAllowed

   .. automethod:: stop

   .. automethod:: wait

   .. automethod:: maw

   .. automethod:: fix

   .. automethod:: release

   .. rubric:: Parameters

   .. parameter:: target : any, read-only

      The last target position of a :meth:`start` operation on the device.

   .. parameter:: fixed : str, not shown to the user

      This parameter is set by :meth:`fix` and :meth:`release` to indicate if
      the device has been fixed.


``Measurable``
==============

.. class:: Measurable

   This class inherits from :class:`Readable` and is the base for all devices
   used for data acquisition (usually detectors).

   .. rubric:: Public methods

   .. automethod:: start

   .. automethod:: stop

   .. automethod:: pause

   .. automethod:: resume

   .. automethod:: duringMeasureHook

   .. automethod:: isCompleted

   .. automethod:: wait

   .. automethod:: save

   .. automethod:: valueInfo

   All :meth:`Measurable.doRead` implementations must return tuples with values
   according to :meth:`valueInfo`.


-------------
Mixin classes
-------------

``HasLimits``
=============

.. class:: HasLimits

   This mixin can be inherited from device classes that are continuously
   moveable.  It automatically adds two parameters, absolute and user limits,
   and overrides :meth:`.isAllowed` to check if the given position is within the
   limits before moving.

   .. note:: In a base class list, ``HasLimits`` must come before ``Moveable``,
      e.g.::

         class MyDevice(HasLimits, Moveable): ...

   .. rubric:: Parameters

   .. parameter:: abslimits : number tuple, mandatory

      Absolute minimum and maximum values for the device to move to, as a tuple.
      This parameter cannot be set after creation of the device and must be
      given in the setup configuration.

   .. parameter:: userlimits : number tuple, optional

      Minimum and maximum value for the device to move to.  This parameter can
      be set after creation, but not outside the ``abslimits``.


``HasOffset``
=============

.. class:: HasOffset

   Mixin class for Readable or Moveable devices that want to provide an 'offset'
   parameter and that can be adjusted via the :func:`adjust` user command.

   A class that provides an offset must inherit this mixin, and subtract or add
   ``self.offset`` in :meth:`doRead` or :meth:`doStart`, respectively.

   .. rubric:: Parameters

   .. parameter:: offset : number, optional

      The current offset of the device zero to the hardware zero.

      The device position is ``hardware_position - offset``.


``HasPrecision``
================

.. class:: HasPrecision

   Mixin class for Readable or Moveable devices that want to provide a
   'precision' parameter.

   .. rubric:: Parameters

   .. parameter:: precision : number, optional

      The precision of the device.
