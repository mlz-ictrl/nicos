.. highlight:: python

Introduction
============

NICOS as an instrument (or experiment) control software knows different types
of entities to control the instrument/experiment:

- :ref:`Devices <nicos_devices>`
- :ref:`Commands <nicos_commands>`
- :ref:`Python control structures and builtin functions <python_controls>`
- :ref:`Variables <nicos_variables>`


.. _nicos_devices:

Devices
-------

In NICOS, devices are simply names.  Each name usually corresponds to a
physical device, like motors, coders, switches, sensors (for temperatures,
pressures, humidity, ...) and so on.

It's possible to define more complex, higher level devices [#fdev1]_, where a
set of physical devices work together in a certain way to read/write a physical
value.  An example is a device to manipulate the incoming wavelength with a
crystal monochromator, where the rotation of the crystal and the position of
the outgoing beam define the used wavelength.

NICOS doesn't differentiate between these types of devices, it instead divides
devices by their functionality.  Some devices can only read a value, some other
can be moved to a certain position, either to any value in range `[min, max]`
or only to a limited number of values (e.g. a switch with `'on'`, `'off'` or
`1`, `0` values).
Detector devices are another fundamental group of devices, which can be
instructed to prepare counting (different type of presets are possible), start
and stop counting, and read out the counter values.

In NICOS the devices are - similar to the reality - objects, which means they
have a set of methods, which can be accessed via the syntax::

   dev.method(list of parameters)

   Examples:

      coder.read()
      motor.move(10)
      motor.stop()

and a set of (configuration) parameters, which can be read and set (if allowed)
at runtime. A parameter value can be read via::

   dev.parameter

and set by::

   dev.parameter = new_value


.. _nicos_commands:

Commands
--------

Commands in NICOS are functions [#cmd1]_ which may require some parameters.
The parameters (type, values, number of parameters, and so on) depend on the
command itself.


.. _python_controls:

Python control structures and builtin functions
-----------------------------------------------

Additionally to the NICOS defined commands and devices the Python
`control structures <https://docs.python.org/3.9/tutorial/controlflow.html>`_
(such as e.g. `if`) and
`builtin functions <https://docs.python.org/3.9/library/functions.html>`_
(e.g. `abs`) are available and can be used.


.. _nicos_variables:

Variables
---------

As in regular Python, a variable name can be of any length and has to consist
of ASCII letters (A-Z, and a-z ), digits (0-9), and the underscore character
(_), but it's not allowed to start with a digit.

The variables may be set in interactive mode and in scripts.

.. warning::

   NICOS defined names are not allowed to be overriden.  When trying to
   override them, NICOS generates an error message.

.. [#fdev1] Sometimes such devices are also known as "virtual motors".
.. [#cmd1] Internally the commands are Python functions and have therefor the
           same syntax.
