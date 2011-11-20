=========
NICOS API
=========

Exceptions
==========

.. module:: nicos.errors

The :mod:`nicos.errors` module defines several exceptions that are used
throughout the system.

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

.. autoexception:: FixedError()

.. autoexception:: CacheLockError()
