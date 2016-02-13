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
      It maps the "internal name" to the type of the device (which usually is
      an abstract type), and a string describing the purpose of the device.

      For example::

         attached_devices = {
             'motor': Attach('the motor to move', nicos.devices.abstract.Motor),
             'coder': Attach('The coder for reading position', nicos.devices.abstract.Coder),
         }

      The actual attached devices for a specific instance (given in the
      instance's configuration) are then type-checked against these types.
      See :class:`~nicos.core.params.Attach` for the full syntax and options.

      During device creation, attached devices are stored as a mapping of
      internal device name to the attached device itself as Device._adevs.
      Attached devices also contain a set Devices._sdevs which contains
      the names of devices using this particular device as an
      attached device (two way linkage).

      Each attached device is also available as an attribute of the Device, but
      prefixed with ``_attached_`` (e.g. ``_attached_motor``).  Be aware that
      these attributes can also be lists of devices, if the Attach option
      ``multiple`` is set.

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

   .. automethod:: history

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
      presented to users, nor created automatically.  Default is: ``False``.

   .. parameter:: loglevel : string, optional

      The loglevel for output from the device.  This must be set to one of the
      loglevel constants.  Default is: ``'info'``.

   .. parameter:: classes : list of strings

      A list of all classes (and mixins) in the class tree of this device.
      For example, for a `Moveable` device this includes
      ``'nicos.core.device.Device'``, ``'nicos.core.device.Readable'`` and
      ``'nicos.core.device.Moveable'``.  This is set automatically by NICOS and
      should not be configured in the setup.

      The parameter is used for introspection e.g. by the GUI: it can decide
      which GUI elements to offer for this device depending on its base classes.

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

   .. attribute:: _attached_<name>

      Each entry of the _adevs dictionary is (with an "_attached_" prefix) also
      available directly as an attribute.  Be aware that these attributes can
      also be lists of devices, if the Attach option multiple is set.

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

   .. rubric:: Parameters

   .. parameter:: fmtstr : string, optional

      A string format template that determines how :meth:`format` formats the
      device value.  The default is ``'%s'``.

   .. parameter:: unit : string, mandatory

      The unit of the device value.

   .. parameter:: maxage : float or None, optional

      The maximum age of cached values from this device, in seconds.  Default is:
      5 seconds.

      If set to ``0``, cached values are never used.  If set to ``None``, values
      are cached indefinitely.

   .. parameter:: pollinterval : float or None, optional

      The interval for polling this device from the :dfn:`NICOS poller`.
      Default is: 6 seconds.

      Can be ``None`` to disable polling.

   .. parameter:: warnlimits : None, or a 2-tuple of any type

      Lower and upper limits of a range in which the device value is allowed to
      be in normal operation. If specified, warnings may be triggered when
      it is outside these values.
      In contrast to `HasLimits.abslimits` and `HasLimits.userlimits`, all valuetypes are allowed
      and the check is based on the default python comparisons, i.e normally
      ``warnlimits[0] <= value <= warnlimits[1]`` should be true.


``Waitable``
============

.. class:: Waitable

   This class inherits from :class:`Readable` and is the base class for all
   devices that have some action that can be waited upon (movement or
   measuring).

   .. automethod:: isCompleted

   .. automethod:: finish

   .. automethod:: _getWaiters

   .. automethod:: wait

      This is implemented using :func:`nicos.core.utils.multiWait`.

   .. automethod:: estimateTime


``Moveable``
============

.. class:: Moveable

   This class inherits from :class:`Waitable` and is the base class for all
   devices that can be moved to different positions (continuously or
   discretely).

   .. automethod:: start

   .. attribute:: valuetype

      This attribute gives the type of the device value, as in the ``type``
      parameter property.  It is used for checking values in :meth:`start`.

   .. automethod:: isAllowed

   .. automethod:: stop

   .. automethod:: maw

   .. automethod:: fix

   .. automethod:: release

   .. rubric:: Parameters

   .. parameter:: target : any, read-only

      The last target position of a :meth:`start` operation on the device.

   .. parameter:: fixed : str, not shown to the user

      This parameter is set by :meth:`fix` and :meth:`release` to indicate if
      the device has been fixed.

   .. parameter:: fixedby : None or tuple of (name, level), not shown to user

      This parameter is set by :meth:`fix` and :meth:`release` to indicate which
      user did the fixing.  Using the daemon-client shell, the :ref:`user level
      <userlevels>` determines if another user may release a fixed device (so
      that devices fixed by ADMIN users are not releasable by USERs).

   .. parameter:: requires : dict

      A dictionary of requirements, similar to the arguments of
      :func:`.requires`.  For access control in the daemon-client shell,
      e.g. you can use ``requires = {'level': 'admin'}`` to restrict write
      actions to ADMIN users.


``Measurable``
==============

.. class:: Measurable

   This class inherits from :class:`Waitable` and is the base for all devices
   used for data acquisition (usually detectors).

   .. rubric:: Public methods

   .. automethod:: setPreset

   .. automethod:: start

   .. automethod:: stop

   .. automethod:: pause

   .. automethod:: resume

   .. automethod:: duringMeasureHook

   .. automethod:: save

   .. automethod:: valueInfo

   .. automethod:: presetInfo

   .. automethod:: prepare

   All :meth:`Measurable.doRead` implementations must return tuples with values
   according to :meth:`valueInfo`.


----------------------
Special device classes
----------------------

``DeviceAlias``
===============

.. autoclass:: DeviceAlias()


``NoDevice``
============

.. autoclass:: NoDevice()


-------------
Mixin classes
-------------

Mixin classes are helper classes to add some special functionality.  They
normally will be inherited together with one of the base classes to implement
new device classes.  This technique avoids the multiplying of a lot of
lines of code.  Besides the functions they also provide the needed parameters.

In the list of the base classes the mixin classes **must** be written before
the base device classes.

Assuming we want to create a new device class, called ``MyDevice`` which should
be a `Moveable` and having limits, inherites the `HasLimits` and `Moveable`
classes.

.. code-block:: python

   class MyDevice(HasLimits, Moveable): ...


..
   Mixin classes are contained in :mod:`nicos.core.mixins` and re-exported in
   :mod:`nicos.core`.

.. module:: nicos.core.mixins

``DeviceMixinBase``
===================

.. autoclass:: DeviceMixinBase()


``HasLimits``
=============

.. autoclass:: HasLimits()


``HasOffset``
=============

.. autoclass:: HasOffset()


``HasPrecision``
================

.. autoclass:: HasPrecision()


``HasMapping``
==============

.. autoclass:: HasMapping()


``HasTimeout``
==============

.. autoclass:: HasTimeout()


``HasWindowTimeout``
====================

.. autoclass:: HasWindowTimeout()


``HasCommunication``
====================

.. autoclass:: HasCommunication()


.. module:: nicos.devices.abstract

``CanReference``
================

.. autoclass:: CanReference()

.. module:: nicos.devices.generic.detector

``TimerChannelMixin``
=====================

.. autoclass:: TimerChannelMixin()

``CounterChannelMixin``
=======================

.. autoclass:: CounterChannelMixin()

``ImageChannelMixin``
=====================

.. autoclass:: ImageChannelMixin()


.. module:: nicos.core.image

``ImageProducer``
=================

.. autoclass:: ImageProducer()


.. module:: nicos.devices.generic.sequence

``SequencerMixin``
==================

.. autoclass:: SequencerMixin()
