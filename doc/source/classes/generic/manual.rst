Manual moveable classes
=======================

Manual *moveable* devices are not connected to any hardware.  The intention of
this group of devices is to have a possibility to include some instrument
parameters which could not be read by electronic means into the control
software.  Examples:

- distance between source and sample (manual move)
- presence or absence of components like filters (manual switch)


.. module:: nicos.devices.generic.manual

.. autoclass:: ManualMove()

.. autoclass:: ManualSwitch()
