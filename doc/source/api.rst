=================
Further NICOS API
=================

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

.. autoexception:: ProgrammingError()

.. autoexception:: PositionError()

.. autoexception:: MoveError()

.. autoexception:: LimitError()

.. autoexception:: CommunicationError()

.. autoexception:: TimeoutError()

.. autoexception:: HardwareError()

.. autoexception:: FixedError()

.. autoexception:: CacheLockError()


Parameter definition
====================

.. module:: nicos.core.params

The :mod:`nicos.core.params` module defines various helpers that are used when
writing device classes.  They are re-exported in :mod:`nicos.core`.

.. autoclass:: Param(description, type=float, default=_notset, mandatory=False, settable=False, volatile=False, unit=None, category=None, preinit=False, prefercache=None, userparam=True)

.. autoclass:: Override(**keywords)

.. autoclass:: Value

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

.. function:: vec3

   Converter that only accepts 3-vectors (i.e. lists or tuples) of floats.

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

.. function:: oneof(converter, *values)

   Create a converter that accepts only one of the given *values* after
   conversion by the *converter*.  Example::

       Param(..., type=oneof(str, 'up', 'down'))

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
