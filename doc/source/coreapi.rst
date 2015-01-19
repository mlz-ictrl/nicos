=================
Further NICOS API
=================

.. module:: nicos.core

Most API elements described here are used when writing new device classes.  They
are defined in submodules of :mod:`nicos.core`, but re-exported in
:mod:`nicos.core` for easier importing.

Exceptions
==========

.. module:: nicos.core.errors

The :mod:`nicos.core.errors` module defines several exceptions that are used
throughout the system.  They are re-exported in :mod:`nicos.core`.

The following exceptions can be used when writing custom devices:

.. autoexception:: NicosError()

.. autoexception:: InvalidValueError()

.. autoexception:: UsageError()

.. autoexception:: ConfigurationError()

.. autoexception:: ModeError()

.. autoexception:: AccessError()

.. autoexception:: ProgrammingError()

.. autoexception:: PositionError()

.. autoexception:: MoveError()

.. autoexception:: LimitError()

.. autoexception:: CommunicationError()

.. autoexception:: TimeoutError()

.. autoexception:: HardwareError()

.. autoexception:: CacheLockError()


Parameter definition
====================

.. module:: nicos.core.params

The :mod:`nicos.core.params` module defines various helpers that are used when
writing device classes.  They are re-exported in :mod:`nicos.core`.

.. autoclass:: Param(description, type=float, default=_notset, mandatory=False, settable=False, volatile=False, unit=None, category=None, preinit=False, prefercache=None, userparam=True, chatty=False)

.. autoclass:: Override(**keywords)

.. autoclass:: Value

.. autoclass:: Attach(self, description, devclass, optional=False, multiple=False)

.. data:: INFO_CATEGORIES

   The categories allowed for `.Device.info()` are:

   * ``'experiment'`` -- Experiment information
   * ``'sample'`` -- Sample and alignment information
   * ``'instrument'`` -- Instrument setup
   * ``'offsets'`` -- Offsets
   * ``'limits'`` -- Limits
   * ``'precisions'`` -- Precisions
   * ``'status'`` -- Instrument status (reserved for `status()` values)
   * ``'general'`` -- Instrument state, i.e. everything else of importance


Converter functions
-------------------

These functions can be used to create parameter types (i.e. the *type* argument
of `Param`) that not only convert to the correct type (such as `int`, `str`
etc.), but also do more validation of the parameter.

.. function:: anytype

   Converter that accepts anything.  Example::

       Param(..., type=anytype)

.. function:: tacodev

   Converter that only accepts valid TACO device names.

.. function:: tangodev

   Converter that only accepts valid TANGO device names.

.. function:: vec3

   Converter that only accepts 3-vectors (i.e. lists or tuples) of floats.

.. function:: limits

   Converter that only accepts a list or tuple of two values, where the second
   value must be greater than the first value.  The first value will be used as
   a lower limit and the second as an upper limit.  Example::

       Param(..., type=limits)

.. function:: mailaddress

   Converter that accepts only valid email addresses, but without a check for
   the existence of the mailaddress itself.  Example::

       Param(..., type=mailaddress)

.. function:: intrange(from, to)

   Create a converter that accepts only integers in the ``range(from, to)``
   (i.e., *to* is excluded).

.. function:: floatrange(from, to)

   Create a converter that accepts only floats between *from* and *to*.
   Examples::

       Param(..., type=floatrange(0, 10))

.. function:: none_or(converter)

   Create a converter that accepts only ``None`` or what the *converter*
   accepts.  Example::

       Param(..., type=none_or(str))

.. function:: oneof(*values)

   Create a converter that accepts only one of the given *values*.  Example::

       Param(..., type=oneof('up', 'down'))

.. function:: listof(element_converter)

   Create a converter that accepts only lists with element types given by the
   *element_converter*.  Examples::

       Param(..., type=listof(int))
       Param(..., type=listof(tacodev))

.. function:: nonemptylistof(element_converter)

   Like `listof`, but the list may not be empty.

.. function:: tupleof(*element_converters)

   Create a converter that accepts only tuples with element types given by the
   *element_converters*.  Examples::

       Param(..., type=tupleof(int, int))
       Param(..., type=tupleof(tacodev, str, str))

.. function:: dictof(key_converter, value_converter)

   Create a converter that accepts only dictionaries with key types given by
   *key_converter* and value types given by *value_converter*.

.. function:: oneofdict(values)

   Create a converter that accepts only the keys and values of the dictionary
   given in *values*.  When one of the keys is given, it is converted to the
   corresponding value.  Example::

       Param(..., type=oneofdict({'up': 1, 'down': 0}))


Status values
=============

.. module:: nicos.core.status

The :mod:`nicos.core.status` module defines the status constants that are used
as the first item of the tuple that `.Device.status` returns.  The whole
`status` module is re-exported in :mod:`nicos.core`.

.. data:: OK

   The device is in a ready or idle state with no errors.

.. data:: BUSY

   The device is in a busy state (moving or waiting for completion).

.. data:: NOTREACHED

   The device has not reached its target/setpoint.

.. data:: ERROR

   The device is in an error state.

.. data:: UNKNOWN

   The state of the device is not known.

.. data:: statuses

   A dictionary mapping these status values, which are integers, to their
   lowercased name (i.e., ``statuses[ERROR] == 'error'``).


Utilities
=========

.. currentmodule:: nicos.core.device

The :mod:`nicos.core.device` module defines some decorators for device methods:

.. autofunction:: usermethod

.. autofunction:: requires

.. module:: nicos.core.utils

The :mod:`nicos.core.utils` module also defines some utility functions.  They
are re-exported in :mod:`nicos.core`.

.. autofunction:: defaultIsCompleted

.. autofunction:: multiStatus

.. autofunction:: multiIsCompleted

.. autofunction:: multiWait

.. autofunction:: waitForStatus

.. autofunction:: multiStop

.. autofunction:: multiReset


Classes for image handling
==========================

.. module:: nicos.core.image

.. XXX document ImageSink, ImageInfo, ImageType

.. autoclass:: ImageProducer()


Writing commands
================

.. module:: nicos.commands

Writing a custom user command is easy: just write a normal function and apply
the `usercommand` decorator.  The docstring of the function is the help for the
command.  A user command should raise `.UsageError` when used improperly: the
command help is shown automatically when such an error is raised.

In order to make user commands available in the NICOS namespace, they must be in
a module that is mentioned by a `modules` list in a loaded setup (see
:ref:`setups`).

.. autofunction:: usercommand
