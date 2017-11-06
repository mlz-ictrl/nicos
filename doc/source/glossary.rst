========
Glossary
========

.. glossary::

   attached device
      Each NICOS device can depend on other devices of which only the interface
      is specified.  In this way, subcomponents with the same interface can be
      replaced without a change of the device code.  Attached devices are
      declared in device classes in a `nicos.core.device.Device.attached_devices`
      dictionary and configured in setup files like regular parameters.

   cache
      The NICOS cache is a service that should run once for every instrument.
      It provides caching of values and parameters from NICOS devices, access
      locking and history archival.  Every NICOS session can connect to this
      cache, and is automatically synchronized with other sessions via this
      cache connection.

   cache lock
      For devices that need to synchronize access to hardware between multiple
      processes, the cache provides a locking mechanism.  It is used like a
      Python lock using the methods :meth:`.Device._cachelock_acquire` and
      :meth:`.Device._cachelock_release`.

   execution mode
      A NICOS :term:`session` can be in one of four execution modes:

      * **master** -- all commands are allowed.  Only one master session can
        be active at the same time.
      * **slave** -- only commands that don't change the instrument state are
        allowed, e.g. reading positions and parameters.  There can be several
        slave sessions active at the same time.
      * **maintenance** -- all commands are allowed, and this mode can be
        activated even if there is another session in master mode.  This is
        strictly meant for maintenance purposes.
      * **simulation** -- all commands are allowed, but the session does not
        talk to the actual hardware ("dry-run mode").  All commands run actual
        code as far as possible, but skip over hardware accessing code.

      The :term:`cache` tracks the current master session and only allows one
      such session at each time.

      The current execution mode is available as the ``_mode`` attribute on
      every device instance.

   fix
      Using the :func:`.fix` user command, a device is locked for further "move"
      commands.  :func:`.release` releases the fix.

   master
      The NICOS session that is currently in master mode (see :term:`execution
      mode`).  I.e. the session controlling the instrument.

   parameter
      A property/attribute of a NICOS device.

   session
      Each instance of a program that creates NICOS objects (and possibly allows
      the user to execute commands on them) is called a session.

   session object
      A singleton instance of a subclass of :class:`nicos.core.sessions.Session`
      that collects all important information from a :term:`session`.

   setup
      A NICOS setup is a collection of configuration data (mostly configuration
      of devices) that represents a part of an instrument configuration.  Every
      NICOS session has one or more setups loaded.  Setups can depend on other
      setups, so that different instrument configurations can share common
      devices easily.

      Setups are described in detail here: :ref:`setups`.

   user command
      A Python function that is meant to be executed by the user.  It is created
      using the :func:`.usercommand` decorator, and must be placed in a module
      that is mentioned by the ``modules`` entry in a :term:`setup`.
