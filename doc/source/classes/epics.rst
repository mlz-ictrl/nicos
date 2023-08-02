.. _epics:

EPICS classes
=============

.. note::

   The EPICS Python module must be imported in the main threads
   of :ref:`daemon <daemon>` and :ref:`poller <poller>` services before it can
   be accessed by any device.
   This can be achieved by adding the following line::

      import nicos.devices.epics.pyepics

   to the :ref:`startupcode <setup-startupcode>` section of the
   :ref:`daemon <daemon>` and :ref:`poller <poller>` setups.


.. module:: nicos.devices.epics.pyepics

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

.. module:: nicos.devices.epics.pva.caproto
.. autoclass:: CaprotoWrapper()

.. module:: nicos.devices.epics.pva.p4p
.. autoclass:: P4pWrapper()

Specific classes using one or more PVs
--------------------------------------

.. currentmodule:: nicos.devices.epics.pva
.. autoclass:: EpicsReadable()

.. autoclass:: EpicsMoveable()

.. autoclass:: EpicsStringReadable()

.. autoclass:: EpicsStringMoveable()

.. autoclass:: EpicsAnalogMoveable()

.. autoclass:: EpicsDigitalMoveable()

.. autoclass:: EpicsMappedMoveable()
