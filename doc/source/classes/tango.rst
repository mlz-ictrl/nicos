Tango classes
=============

.. module:: nicos.devices.tango

Basic Tango binding (PyTango)
-----------------------------

.. autoclass:: PyTangoDevice()

FRM II/JCNS interface bindings
------------------------------
These classes only support devices which fulfill the official FRM-II/JCNS TANGO interface.
For more information about the interfaces, have a look at: https://forge.frm2.tum.de/tango/interfaces/

.. autoclass:: AnalogInput()

.. autoclass:: Sensor()

.. autoclass:: AnalogOutput()

.. autoclass:: Actuator()

.. autoclass:: Motor()

.. autoclass:: TemperatureController()

.. autoclass:: DigitalInput()

.. autoclass:: DigitalOutput()

.. autoclass:: StringIO()

