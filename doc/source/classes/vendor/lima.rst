Lima devices
============

.. module:: nicos.devices.vendor.lima

These classes use the **L**\ ibrary of **Im**\ age **A**\ cquisition for unified
controlling of 2D detectors.


Generic devices
---------------

.. autoclass:: GenericLimaCCD()


Hardware specific extensions
----------------------------

The following classes are extensions to the GenericLimaCCD class or additional classes
that provide access to hardware specific functions via Lima.

Andor2
~~~~~~
The following classes are specific to cameras produced by Andor (https://www.andor.com/) and based on version 2 of their camera SDK.

.. autoclass:: Andor2LimaCCD()

.. autoclass:: Andor2TemperatureController()

