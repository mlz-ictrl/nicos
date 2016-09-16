Manual moveable classes
=======================

Manual *moveable* devices are not connected to any hardware.  The intension of
this group of devices is to have a possibility to include some instrument
parameters which could not be read by any electronic device into the control
software.  Examples:

- distances between monochromator and sample
- distances between source and sample
- ...

.. module:: nicos.devices.generic.manual

.. autoclass:: ManualMove()

.. autoclass:: ManualSwitch()
