.. Core NICOS concepts
   ===================

   Device types
   ------------

   Most devices in NICOS are based on a few "core" devices which define their
   basic behaviour:

   * :class:`Readable <nicos.core.device.Readable>`

     A device which periodically reads a value from somewhere (e.g. a temperature
     sensor).
   * :class:`Waitable <nicos.core.device.Waitable>`

     A `Readable` which can execute some action and wait for its completion. It
     is usually used as a "controller" device for other devices, for example
     multiple motors which move together. The controller device can initiate the
     combined movement via a custom command and then be waited upon until all
     "attached" devices have completed their individual movements.
   * :class:`Moveable <nicos.core.device.Moveable>`

     A `Waitable` which can start a "movement" in order to change a particular
     value.

     A typical example would be a motor or a temperature controller.
   * :class:`Measurable <nicos.core.device.Measurable>`

     A `Waitable` for acquiring data. The data acquisition is "started" via the
     :func:`count <nicos.commands.measure.count>` or by one of the
     :ref:`scan commands <scanning_commands>`.

     A typical example would be a detector.

   These core devices are located in :mod:`nicos.core.device`. See their
   respective docstrings for more.
