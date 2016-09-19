.. _write-a-new-device:

Writing a new device class
==========================

Although NICOS already contains a lot of device classes, it is usually necessary
to create new device classes for specialized tasks.  This *tutorial* should help
you to do it in a NICOS like way.

But, first of all have a deep look into the :doc:`existing devices classes
<../classes/index>` to see if they would fulfill your requirements.  Please bear
in mind that most of the devices have a number of parameters which can be
configured in a setup file.

Sometimes there exists a device class which is very similiar to your requests,
but not fully.  In this case you can derive your device class from the existing
one, implementing the missing parts or overriding one or more of the base class
methods.  It might also be reasonable to make the existing class more generic,
to fit more use cases -- feel free to submit patches to these classes.

If all this doesn't help you have to add a device class.

In NICOS all devices are categorized into mainly three groups:

* :class:`~nicos.core.device.Readable`
* :class:`~nicos.core.device.Moveable`
* :class:`~nicos.core.device.Measurable`

which are organized in class hierarchy:

.. inheritance-diagram:: nicos.core.device.Device nicos.core.device.Readable
                         nicos.core.device.Waitable nicos.core.device.Moveable
                         nicos.core.device.Measurable
   :parts: 1

First you have to select one of the basic types the new device class should be.


Defining parameters
-------------------

To use a device in instrument control it must normally configured.  This task is
the job of the parameters in NICOS.  Each of the device classes has a
dictionary, called ``parameters``, where all parameters specific to this
subclass are added.  All base class parameters are automatically inherited.
Parameter definitions are made using the :class:`~nicos.core.params.Param`
helper.  The job of the developer is to choose the right parameter name(s) and
type(s) for the device.

Currently, each parameter definition has to be made at programming time.
Besides a short and an extended description, the type, the visibility, a
possible default value, a possible unit, and some other definitions have to be
made.  It is also selected if a user may change the parameter value at runtime.

.. code::

   parameters = {
       'myparam': Param('A short parameter description',
                        type=str),
   }


Overriding inherited parameters
-------------------------------

Sometimes the inherited class has a parameter definition, which is not exactly
fulfilling the requirements of the new device.  For this case there is another
dictionary called ``parameter_overrides``.

It needs the name of the paramter to be changed and instead of using the
:class:`~nicos.core.params.Param` the :class:`~nicos.core.params.Override`
helper is used, which is only given the settings of the parameter to be
overridden.

.. code::

   class BaseDevice(...):

       parameters = {
           'parameter1': Param('description ... ', settable=True,
                               type=int, default=10),
           ...
       }

   class DerivedDevice(..., BaseDevice):

       parameter_overrides = {
           'parameter1': Override(type=intrange(0, 4), default=1),
       }


Using other NICOS devices
-------------------------

In case the new device class should represent a more high level device, like a
slit with for blades or device that has to control two motors, it is needed to
use other configured devices.  This can be defined in the ``attached_devices``
dictionary.  It contains an internal device name (accessible via
``self._attached_name`` where ``name`` has to be replaced by the choosen name
and an object of the :class:`~nicos.core.params.Attach` helper.

.. code::

   class SlitDevice(...):

       attached_devices = {
          'leftblade': Attach('Left blade moving device', Moveable),
       }

Any setup that configures a ``SlitDevice`` now also has to configure its
``leftblade`` attached device (like a mandatory parameter).

In the previous example the access to the ``leftblade`` device is::

   self._attached_leftblade

There are several parameters to :class:`~nicos.core.params.Attach` that specify
what types of and how many devices are allowed.  Attached devices can be made
optional.


Deriving from abstract classes
------------------------------

There are some :doc:`abstract classes <../classes/abstract>` designed for use as
base classes to implement specific functionality.

.. todo::
   explain and example


Combining with mixins
---------------------

Before writing new functionality which is very often used you should have a look
into the :ref:`mixin classes <mixin-classes>`.  They provide a lot of reusable
functionality.

.. todo::
   explain and example
