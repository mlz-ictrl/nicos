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
