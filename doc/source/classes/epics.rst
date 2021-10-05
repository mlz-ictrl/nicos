EPICS classes
=============

.. module:: nicos.devices.epics

Basic EPICS binding mixin (pyepics)
-----------------------------------

.. autoclass:: EpicsDevice()

Specific classes using one or more PVs
--------------------------------------

.. autoclass:: EpicsReadable()

.. autoclass:: EpicsMoveable()

.. autoclass:: EpicsStringReadable()

.. autoclass:: EpicsStringMoveable()

.. autoclass:: EpicsAnalogMoveable()

.. autoclass:: EpicsDigitalMoveable()

.. autoclass:: EpicsWindowTimeoutDevice()


Dual protocol bindings
----------------------

.. module:: nicos.devices.epics.pva

Basic EPICS binding mixin
-------------------------

Allows specify which EPICS protocol to use.


.. autoclass:: EpicsDevice()

Wrapper classes for EPICS protocols
-----------------------------------

.. autoclass:: CaprotoWrapper()

.. autoclass:: P4pWrapper()

Specific classes using one or more PVs
--------------------------------------

.. autoclass:: EpicsReadable()

.. autoclass:: EpicsMoveable()

.. autoclass:: EpicsStringReadable()

.. autoclass:: EpicsStringMoveable()

.. autoclass:: EpicsAnalogMoveable()

.. autoclass:: EpicsDigitalMoveable()

.. autoclass:: EpicsMappedMoveable()
