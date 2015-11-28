Session API reference
=====================

.. module:: nicos.core.sessions

The "NICOS session" object is a singleton instance that provides all global
operations to any shell or daemon that uses NICOS devices.  Its functions
include the management of

* setups: loading and unloading setups
* devices: creating and shutting down devices
* special devices: providing access to special device instances
* namespace:
* the execution mode: switching modes
* logging: handling the various NICOS loggers
* notifications: sending notifications from devices or user code

.. autoclass:: Session

   **Global configuration**

   .. attribute:: config

      A singleton for settings read from ``nicos.conf``.  See :ref:`nicosconf`.

   .. attribute:: autocreate_devices

      A boolean that determines if the session automatically creates all
      non-`.lowlevel` devices in a setup (if true), or if devices are created
      on-demand by calls to `getDevice` (if false).

   .. attribute:: cache

      The NICOS cache client.


   **Mode handling**

   .. autoattribute:: mode
   .. automethod:: setMode


   **Logging**

   .. attribute:: log

      This is the root logger object.  All output that is not specific to a
      device should be emitted using this logger.  (The commands in
      :mod:`nicos.commands.output` also use this logger.)

   .. automethod:: getLogger
   .. automethod:: addLogHandler
   .. automethod:: logUnhandledException


   **Setup handling**

   .. automethod:: setSetupPath
   .. automethod:: getSetupPath
   .. automethod:: getSetupInfo

      See :ref:`setups`.

   .. automethod:: loadSetup
   .. automethod:: unloadSetup
   .. automethod:: handleInitialSetup
   .. automethod:: shutdown


   **Namespace management**

   The NICOS namespace is the namespace in which user code should be executed.
   Objects exported into the NICOS namespace are protected from overwriting by
   the user.

   .. automethod:: export
   .. automethod:: unexport
   .. automethod:: getExportedObjects

   **Devices**

   .. automethod:: getDevice
   .. automethod:: createDevice
   .. automethod:: destroyDevice

   **Special devices**

   .. attribute:: instrument

      The instrument device configured for the current setup.  An instance of (a
      subclass of) `nicos.devices.instrument.Instrument`.

   .. attribute:: experiment

      The experiment device configured for the current setup.  An instance of (a
      subclass of) `nicos.devices.experiment.Experiment`.

   .. attribute:: notifiers

      The notifier devices configured for the current setup.  A list of
      instances of `nicos.devices.notifiers.Notifier`.

   .. attribute:: datasinks

      The data sinks configured for the current setup.  A list of instances of
      `nicos.core.data.DataSink`.


   **Notification support**

   .. automethod:: notify
   .. automethod:: notifyConditionally

   **Miscellaneous**

   .. automethod:: commandHandler

   **Session-specific behavior**

   These methods should be overridden in subclasses.

   .. automethod:: breakpoint
   .. automethod:: updateLiveData
   .. automethod:: checkAccess
