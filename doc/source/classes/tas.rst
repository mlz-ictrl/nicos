Triple-Axis spectrometer classes
================================

These classes are specific to the operation of triple-axis spectrometers.

All classes described here are re-exported in the :mod:`nicos.tas` module, so
for example both ``nicos.tas.Monochromator`` and
``nicos.tas.mono.Monochromator`` are valid entries for the class name in a setup
file.

.. module:: nicos.tas.mono

.. autoclass:: Monochromator()

.. module:: nicos.tas.spectro

.. autoclass:: TAS()

.. module:: nicos.tas.cell

.. autoclass:: TASSample()
