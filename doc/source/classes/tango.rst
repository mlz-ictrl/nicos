Tango classes
=============

.. module:: nicos.devices.tango

Basic Tango binding (PyTango)
-----------------------------

.. autoclass:: PyTangoDevice()

MLZ interface bindings (Entangle)
---------------------------------
These classes only support devices which fulfill the official MLZ TANGO
interface.

For more information about the interfaces, please have a look at:
https://forge.frm2.tum.de/entangle/defs/entangle-master/

.. module:: nicos.devices.entangle

.. autoclass:: AnalogInput()

.. autoclass:: Sensor()

.. autoclass:: AnalogOutput()

.. autoclass:: WindowTimeoutAO()

.. autoclass:: Actuator()

.. autoclass:: Motor()

.. autoclass:: RampActuator()

.. autoclass:: TemperatureController()

.. autoclass:: PowerSupply()

.. autoclass:: DigitalInput()

.. autoclass:: NamedDigitalInput()

.. autoclass:: PartialDigitalInput()

.. autoclass:: DigitalOutput()

.. autoclass:: NamedDigitalOutput()

.. autoclass:: PartialDigitalOutput()

.. autoclass:: VectorInput()

.. autoclass:: VectorInputElement()

.. autoclass:: VectorOutput()

.. autoclass:: OnOffSwitch()

.. autoclass:: StringIO()

.. autoclass:: DetectorChannel()

.. autoclass:: CounterChannel()

.. autoclass:: ImageChannel()

.. autoclass:: TOFChannel()

.. autoclass:: TimerChannel()

