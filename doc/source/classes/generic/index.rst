Generic device classes
======================

These classes are "generic" device classes in that they do not interface with a
specific hardware or system, but rely on attached devices to provide actual
hardware access.  They are generally "superdevices", such as a monochromator
device that controls a theta and a two-theta angle.

All classes described here are re-exported in the :mod:`nicos.devices.generic`
module, so for example both ``nicos.devices.generic.Slit`` and
``nicos.devices.generic.slit.Slit`` are valid entries for the class name in a
setup file.

.. toctree::

   axis
   slit
   switcher
   sequencer
   manual
   detector
   cache
   system
   paramdev
   alias
   virtual
