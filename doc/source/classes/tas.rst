Triple-Axis spectrometer classes
================================

These classes are specific to the operation of triple-axis spectrometers.

All classes described here are re-exported in the :mod:`nicos.devices.tas` module, so
for example both ``devices.tas.Monochromator`` and ``devices.tas.mono.Monochromator``
are valid entries for the class name in a setup file.

.. module:: nicos.devices.tas.mono

.. autoclass:: Monochromator()

.. module:: nicos.devices.tas.spectro

.. autoclass:: TAS()

.. module:: nicos.devices.tas.cell

.. autoclass:: TASSample()

.. module:: nicos.devices.tas.ecradle

.. autoclass:: EulerianCradle()

.. module:: nicos.devices.tas.vgonio

.. autoclass:: VirtualGonio()
