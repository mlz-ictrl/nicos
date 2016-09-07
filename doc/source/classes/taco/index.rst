.. _taco:

============
Taco classes
============

These classes serve to interface with Taco devices.  Generally the corresponding
Taco Python modules need to be installed; for example, the temperature control
classes need the ``Temperature`` module from the ``taco-client-temperature``
package.

For a description of the TACO system at FRM II see `this documentation
<https://forge.frm2.tum.de/wiki/projects:taco:index>`_.

All classes described here are re-exported in the :mod:`nicos.devices.taco` module, so
for example both ``devices.taco.AnalogOutput`` and ``devices.taco.io.AnalogOutput``
are valid entries for the class name in a setup file.

.. toctree::

   core
   detector
   axis
   power
   temperature
   io
