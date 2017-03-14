.. index:: !watchdog, !nicos-watchdog
.. _watchdog:

The Watchdog daemon
===================

The watchdog is a service that monitors value updates from the :ref:`cache
<cache>`, and checks if one of its preconfigured conditions becomes true.  When
that is detected, it can send out notifications and/or run some NICOS commands
(an "action"), or also pause the count loop if supported.


Invocation
----------

The watchdog is invoked by the ``nicos-watchdog`` script.  It should normally be
started by the :ref:`init script <initscript>`.

The watchdog expects a setup file with a device named ``Watchdog``.

.. The file must be named either ``watchdog.py`` or :file:`SETUPNAME.py`, where
   ``SETUPNAME`` is a user-defined name.

On startup using the ``nicos-watchdog`` executable, the setup loaded is either
``watchdog.py`` if started with no arguments, or ``SETUPNAME.py`` if started
with command line arguments ``-S`` or ``--setup``.

There are several command-line options that allow to customize the startup of
the watchdog.

.. program:: watchdog

.. option:: -h, --help

    show the help message and exit

.. option:: -d, --daemon

    daemonize the watchdog process

.. option:: -S SETUPNAME, --setup=SETUPNAME

    name of the setup, default is 'watchdog'


Setup file
----------

The setup file for the watchdog daemon is by default:
``custom/<instrument_name>/setups/special/watchdog``.

A simple setup file for the watchdog could look like this::

  description = 'setup for the NICOS watchdog'
  group = 'special'

  watchlist = [
      dict(condition = 't_value > 300',
           message = 'Temperature too high (exceeds 300 K)',
           type = 'critical',
           gracetime = 10,
           action = 'maw(T, 290)'),
      dict(condition = 'tbefilter_value > 75',
           setup = 'befilter',
           scriptaction = 'pausecount',
           message = 'Beryllium filter temperature too high',
           gracetime = 0),
      dict(condition = 'shutter_value == "closed"',
           type = '',
           scriptaction = 'pausecount',
           message = 'Instrument shutter is closed',
           gracetime = 0),
      dict(condition = 'reactorpower_value < 15',
           precondtion = 'reactorpower_value > 19',
           precondtime = 600,
           gracetime = 120,
           setup = 'reactor',
           message = 'reactor power loss',
           scriptaction = 'stop'),
  ]

  devices = dict(

      mailer   = device('devices.notifiers.Mailer',
                        sender = 'root@demo'),

      smser    = device('devices.notifiers.SMSer',
                        receivers = ['01721234567']),

      Watchdog = device('services.watchdog.Watchdog',
                        cache = 'localhost:14869',
                        notifiers = {'default': ['mailer'],
                                     'critical': ['mailer', 'smser']},
                        watch = watchlist,
                       ),
  )

The parameter ``cache`` must point to the ``host:port`` address of the cache to
connect to.

The most important parameter for the ``Watchdog`` device is the ``watch`` list.
It is a list of dictionaries, each of which specifies one condition.  The
specification can have these keys:

**condition**
   The condition to check.  It typically includes a device value, specified as a
   lowercased cache key with '/' replaced by '_' (so ``t_value`` is the value of
   device ``T``, ``t_setpoint`` is the value of the parameter ``T.setpoint`` and
   so on).

   The condition uses Python syntax, so you can use comparison operators (``>``,
   ``>=``, ``==``, ``!=``, ``<=``, ``<``), mathematical operators like ``+``,
   boolean operators (``and`` and ``or``), and group using parentheses.  A
   complex condition might look like this::

     condition = '(ana_value > 1.58 and befilter == "ana") or (mono_value > 1.58 and befilter == "mono")'

   To check for device status, remember that the status parameter is a tuple of
   a status code and a string.  The status codes can be used with their symbolic
   names::

     condition = '(ana_status[0] == OK) and ("limit switch" not in ana_status[1])'

**setup**
   If present, the name of a setup that must be loaded in the NICOS master for
   this condition to be active.  By default, the condition is always active.

**gracetime**
   The time, in seconds, which the watchdog waits after a condition becomes true
   until a warning is emitted.  If the condition becomes false again during the
   gracetime, no warning is emitted.  The default gracetime is 5 seconds.

**precondition**
   If present, this condition must be fullfiled for at least ``precondtime``,
   before condition will trigger.  The default is no precondition.  The syntax
   is the same as for ``condition``.

**precondtime**
   The time a precondition must be fulfilled. Default is 5 seconds.

**message**
   The message that should be emitted when a warning is generated from the
   condition.  It should be short enough to fit into SMS messages if you want to
   use SMS notifications.

**type**
   The type of the message, default is ``'default'``.

   The ``notifiers`` parameter of the Watchdog device is a dictionary that maps
   type names to a list of notifiers to use for this type.  In the example
   above, the type "default" sends an email, while the type "critical" also
   sends an SMS.  Another use case would be to have two different mail notifiers
   that send mail to different receivers.

   A type of ``''`` does not emit notifications.  This is only useful when
   "scriptaction" is set, see below.

   See :ref:`notifiers` for a list of classes that can be used as notifiers.

**scriptaction**
   This can be set to several different values.  The default is ``''``.

   * ``'pausecount'``: if the condition is detected the NICOS master gets a
     request to pause the count loop, if it is currently in a ``count()``
     operation.  If not, the master will halt at the beginning of the next count
     operation.  When the condition is back to normal, the operation continues.

     This requires all used detectors to support pause/resume.

   * ``'stop'``: if the condition is detected, any script running in the NICOS
     daemon is stopped at the next break point (after a scan step or a command).
     It is not started again when the condition becomes normal.

   * ``'immediatestop'``: if the condition is detected, any script running in
     the NICOS daemon is stopped using the "immediate stop" procedure: stop as
     quickly as possible and execute ``stop()`` on all devices.

**action**
   An action, expressed as NICOS commands, to be executed when the condition is
   detected.  It is run in a separate process, and therefore it can take a few
   seconds until the action is actually executed.  This should not be used for
   very time-critical conditions.

   The action should not take longer than 60 seconds; in case it does the process
   will be forcibly aborted.

Additionally to the actions which could be define the Watchdog may also be used
to send some messages. For this purpose exist some
:ref:`notifier classes <notifiers>`.

.. todo::

   Description of the settings and working mechanism of the notifiers in the
   Watchdog

Server class
------------

.. module:: nicos.services.watchdog

.. autoclass:: Watchdog
