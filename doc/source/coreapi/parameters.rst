Parameter definition
====================

.. currentmodule:: nicos.core.params

The :mod:`nicos.core.params` module defines various helpers that are used when
writing device classes.  They are re-exported in :mod:`nicos.core`.

.. autoclass:: Param(description, type=float, default=_notset, mandatory=False, settable=False, volatile=False, unit=None, category=None, preinit=False, prefercache=None, userparam=True, chatty=False)

.. autoclass:: Override(**keywords)

.. autoclass:: Value

.. autoclass:: Attach(self, description, devclass, optional=False, multiple=False)

.. autoclass:: ArrayDesc

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

.. function:: dictwith(key=value_converter, ...)

   Create a converter that accepts only dictionaries with string keys.  The
   dictionaries must have exactly the keys given to ``dictwith``, and the
   values are converted using the ``value_converter``\s.  For example::

      dictwith(name=str, value=int)

   will accept ``{'name': 'Foo', 'value': 5}`` but not ``{'name': 'Foo'}`` or
   ``{1: 'bar'}``.  ``{'value': 'notanint'}`` will also be rejected.

.. function:: oneofdict(values)

   Create a converter that accepts only the keys and values of the dictionary
   given in *values*.  When one of the keys is given, it is converted to the
   corresponding value.  Example::

       Param(..., type=oneofdict({'up': 1, 'down': 0}))

.. function:: setof

   Create a converter that accepts only sets with element types given by the
   *element_converter*.  Examples::

       Param(..., type=setof(int))
       Param(..., type=setof(tacodev))

.. module:: nicos.core.params

.. autofunction:: nicosdev

.. autofunction:: host

.. autofunction:: nonemptystring

.. autofunction:: pvname

.. autofunction:: ipv4

.. autofunction:: absolute_path

.. autofunction:: relative_path

.. autofunction:: expanded_path

.. autofunction:: subdir

.. autofunction:: string
