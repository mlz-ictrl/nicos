How to write "ideomatic" NICOS code
===================================

Why are the current interface classes a good base
-------------------------------------------------

* Interfaces can be trusted
* Commands can be written in a generic way (independent of device implementation)
* current hierarchy:

.. only:: html

   .. figure:: _static/nicos.svg

..   :target: _static/nicos.svg

Why are there “do” methods for “usermethods”
--------------------------------------------

* Official interfaces are the “user methods”

  * marked with “@usermethod” decorator

* User methods typically implement

  * Value checks
  * Some logic

    * Checking for added mixin’s (i.e. HasLimits, HasPrecision, ...)
    * Checking for fix/release
    * Target checks
    * ...

  * call “do” methods if allowed (check for dry-run-mode)

* “do” methods implement device specific code

  * Targets are valid due to the check in “user method”
  * Attached devices are interfaced by their user methods and parameters!

Why new user methods should have a good reason to exist
-------------------------------------------------------

* Break existing interface(s)
* Not a good idea: „Because of reasons“
* In case there is a need:

  * Try to create a „Mixin“ class to add the new usermethod
    * Easy to check: isinstance
    * Can be easily reused by adding to new classes

Using good parameter types for easier life
------------------------------------------

* Parameters are designed for device configuration
* Determine first the typical value for a parameter
* Select the closest NICOS parameter type needed

  * Wrong configuration parameter values will be found quite early (use of
    check-setup tool) and detected before using
  * Inside the device code the parameter have always valid values
  * Any assignment of invalid values in code will raise an “ConfigurationError”

* Parameters may have their own getter (doRead...) and setter (doWrite...)
  methods

Using the correct value type for devices
----------------------------------------

* Read method should return “consistent” values (no mixture of different types)
* Determine first the typical value(s) for the device 
* Moveable have a class “valuetype” member

  * Similar to type of parameter definition (all parameter types can be used)
  * Any given target will be checked against the valuetype

    * Invalid values raises a “ValueError”

  * Inside the device code doStart the target value is always valid

What are attached devices are good for?
---------------------------------------

* Can be used to write more generic devices

  * Code can be written for all known use cases

* Attachment in configuration (easy)
* Type of attached device (defines available interface), multiplicity,
  optionality can be defined

  * “Attach” type is used
  * Selection of ‘devclass’ should follow the needed user methods and parameters

    * Try to use the closest to base in hierarchy

* Example: Axis

  * One active part (typical any Moveable)
  * One passive part (typical any Readable)
  * Jobs: 

    * Compare current position of Moveable with current value of Readable during
      the movement and at the end
    * Generate retries if not at the target value
    * Abort if difference too high

Dry run and what "hardware_access" means
----------------------------------------

* Dry-Run-Mode allows users to test/verify their commands/scripts before real executing 

  * Test syntax
  * Test limits
  * Makes time estimations
  * device internal: self._mode == SIMULATION

* Code has to be written to support
* “hardware_access” member

  * Defines if there is any direct access to hardware in this device implementation

    * Attached devices may do it, but make their own checking

  * If case set to False:
   
    * all “do” methods will be executed
    * "settable" parameters will be modified, but changes won’t be transferred to cache

Mixins and inheritance
----------------------

* Try to use existing classes
* In case: "not possible"

  * Attempt to inherit
  * Try to use existing mixins to add functionality

    * They are well tested and integrated
    * Less code to write

Parameter overrides
-------------------

* Application: Modify the definition of existing parameter in derived classes
* Try to avoid avoid changes of parameter type
* In principle every definition parameter could be overriden (except name)
* Done with "Override" class

Logging / Debugging output
--------------------------

* Don’t use print()
* use logging and corresponding levels

  * debug
  * info (Standard in NICOS)
  * warning (generates pink colored messages in console)
  * error (generates red colored messages in console)

* For debug output use: self.log.debug

  * At runtime activated by dev.loglevel = ‘debug’ and deactivated by dev.loglevel = ‘info’

* To display information to users use: self.log.info
* Be sparing with the output (users won’t read it finally) as well with warnings
* Errors only if the user should be pointed to real/serious problems -> user friendly

Lazy logging
------------

* Logging should be lazy
* Don’t use f-strings
* Formatting types are the old types
* Logging function tests first the level and make then the formatting (saves time)
  see: https://docs.python.org/3/howto/logging.html

Don't use
---------

* time.sleep

  * use instead :py:func:`session.delay`

Examples
--------

Example 1
^^^^^^^^^

.. code-block:: python
   :linenos:

    parameters = {
        'minimum_rate': Param('Minimum count rate for frame',
                              type=int, settable=True, mandatory=True),
        'rate_monitor': Param('Monitor to check rate against',
                              type=nicosdev, mandatory=True),
        'elapsed_time': Param('Channel to read time from',
                              type=nicosdev, mandatory=True)
    }

    _triggerFinished = None

    def doStart(self):
        self._triggerFinished = None
        if self._attached_followers:
            det = self._attached_followers[0]
            det.start()
            for _ in range(0, 5):
                stat, _ = det.status()
                if stat == BUSY:
                    break
                time.sleep(.3)
            time.sleep(.9)
            # session.log.info('Started CCD\n')
            self._attached_trigger.start()
            # session.log.info('Started Trigger\n')

    def _testRate(self):
        dev = session.getDevice(self.rate_monitor)
        mon = dev.read(0)[0]
        dev = session.getDevice(self.elapsed_time)
        t = dev.read(0)[0]
        if mon < t * self.minimum_rate:
            session.log.info('%s, should %d cts/sec, is %f cts/dec',
                             'Restarting because of insufficient count rate',
                             self.minimum_rate, float(mon)/float(t))
            self.start()
            return False
        else:
            return True

* Lines 21 and 22: Don't use time.sleep, it's not "Dry-Run" safe, use
  `session.delay`
* Lines 23 and 25: Seems to be a debugging output:

  * Change 'info' to 'debug'
  * Don't use 'session.log' in device, instead 'self.log'

    * automatic information about the device, producing the message

  * Don't use CR and/or NL in logging!

.. code-block:: python
   :linenos:

    parameters = {
        'minimum_rate': Param('Minimum count rate for frame',
                              type=int, settable=True, mandatory=True),
        'rate_monitor': Param('Monitor to check rate against',
                              type=nicosdev, mandatory=True),
        'elapsed_time': Param('Channel to read time from',
                              type=nicosdev, mandatory=True)
    }

    _triggerFinished = None

    def doStart(self):
        self._triggerFinished = None
        if self._attached_followers:
            det = self._attached_followers[0]
            det.start()
            for _ in range(0, 5):
                stat, _ = det.status()
                if stat == BUSY:
                    break
                session.delay(.3)
            session.delay(.9)
            self.log.debug('Started CCD')
            self._attached_trigger.start()
            self.log.debug('Started Trigger')

    def _testRate(self):
        dev = session.getDevice(self.rate_monitor)
        mon = dev.read(0)[0]
        dev = session.getDevice(self.elapsed_time)
        t = dev.read(0)[0]
        if mon < t * self.minimum_rate:
            session.log.info('%s, should %d cts/sec, is %f cts/dec',
                             'Restarting because of insufficient count rate',
                             self.minimum_rate, float(mon)/float(t))
            self.start()
            return False
        return True

* Lines 5, 7: Parameter definitions contains `nicosdev` parameter type, hint
  there are other NICOS devices involved
* Lines 28, 31: session.getDevice to get the in line 5 and 7 defined devices,
  but better to use attached devices

  * Make parameter to attached devices
  * Same effort in configuration (single entry)
  * Benefits:

    * Automatic check for existing device in configuration
    * Automatic type check
    * Direct access to the devices (less code → less errors)

.. code-block:: python
   :linenos:

    from nicos.core.params import Attach
    from nicos_sinq.devices.epics.detector import EpicsCounterPassiveChannel, \
        EpicsTimerPassiveChannel

    parameters = {
        'minimum_rate': Param('Minimum count rate for frame',
                              type=int, settable=True, mandatory=True),
    }

    attached_devices = {
        'rate_monitor': Attach('Monitor to check rate against', EpicsCounterPassiveChannel),
        'elapsed_time': Param('Channel to read time from', EpicsTimerPassiveChannel)
    }

    _triggerFinished = None

    def doStart(self):
        self._triggerFinished = None
        if self._attached_followers:
            det = self._attached_followers[0]
            det.start()
            for _ in range(0, 5):
                stat, _ = det.status()
                if stat == BUSY:
                    break
                session.delay(.3)
            session.delay(.9)
            self.log.debug('Started CCD')
            self._attached_trigger.start()
            self.log.debug('Started Trigger')

    def _testRate(self):
        dev = self._attached_rate_monitor.read(0)[0]
        dev = self._attached_elapsed_time.read(0)[0]
        if mon < t * self.minimum_rate:
            session.log.info('%s, should %d cts/sec, is %f cts/dec',
                             'Restarting because of insufficient count rate',
                             self.minimum_rate, float(mon)/float(t))
            self.start()
            return False
        return True
    

Example 2
^^^^^^^^^

.. code-block:: python
   :linenos:

    class MasterSlaveMotor(Moveable):

        ...

        attached_devices = {
            'master': Attach('Master motor controlling the movement', Moveable),
            'slave': Attach('Slave motor following master motor movement', Moveable),
        }

        parameters = {
            'scale': Param('Factor applied to master target position as slave '
                           'position', type=float, default=1),
        }

        parameter_overrides = {
            'unit': Override(mandatory=False),
            'fmtstr': Override(default='%.3f %.3f'),
        }

        def _slavePos(self, pos):
            return self.scale * pos

        def doRead(self, maxage=0):
            return [self._attached_master.read(maxage),
                    self._attached_slave.read(maxage)]

        def doStart(self, target):
            self._attached_master.move(target)
            self._attached_slave.move(self._slavePos(target))

        def doIsAllowed(self, pos):
            faultmsgs = []
            messages = []
            for dev in [self._attached_master, self._attached_slave]:
                allowed, msg = dev.isAllowed(pos)
                msg = dev.name + ': ' + msg
                messages += [msg]
                if not allowed:
                    faultmsgs += [msg]
            if faultmsgs:
                return False, ', '.join(faultmsgs)
            return True, ', '.join(messages)

        def doReadUnit(self):
            return self._attached_master.unit

        def valueInfo(self):
            return Value(self._attached_master.name, unit=self.unit,
                         fmtstr=self._attached_master.fmtstr), \
                   Value(self._attached_slave.name, unit=self.unit,
                         fmtstr=self._attached_slave.fmtstr)

* Target value obvious a float type value (see line 20: multiplication with
  float type parameter)
* Read value (lines 22-24): list type, bad design target value and read valuei
  should have same type!

  * Implementation of 'maw' commands rely on this

.. code-block:: python
   :linenos:

    class MasterSlaveMotor(Moveable):

        ...

        attached_devices = {
            'master': Attach('Master motor controlling the movement', Moveable),
            'slave': Attach('Slave motor following master motor movement', Moveable),
        }

        parameters = {
            'scale': Param('Factor applied to master target position as slave '
                           'position', type=float, default=1),
        }

        parameter_overrides = {
            'unit': Override(mandatory=False),
            'fmtstr': Override(default='%.3f %.3f'),
        }

        valuetype = float

        def _slavePos(self, pos):
            return self.scale * pos

        def doRead(self, maxage=0):
            return [self._attached_master.read(maxage),
                    self._attached_slave.read(maxage)]

        def doStart(self, target):
            self._attached_master.move(target)
            self._attached_slave.move(self._slavePos(target))

        def doIsAllowed(self, pos):
            faultmsgs = []
            messages = []
            for dev in [self._attached_master, self._attached_slave]:
                allowed, msg = dev.isAllowed(pos)
                msg = dev.name + ': ' + msg
                messages += [msg]
                if not allowed:
                    faultmsgs += [msg]
            if faultmsgs:
                return False, ', '.join(faultmsgs)
            return True, ', '.join(messages)

        def doReadUnit(self):
            return self._attached_master.unit

        def valueInfo(self):
            return self._attached_master.valueInfo(), \
                   self._attached_slave.valueInfo()

* "valuetype" changed from `anytype` to float

  * automatic target test, only targets passing the convertion `valuetype(target)`
    will be accepted

* Each attached device has it's own valueInfo() method and should be used
