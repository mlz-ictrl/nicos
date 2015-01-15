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

-h, --help                       show the help message and exit
-d, --daemon                     daemonize the watchdog process
-S SETUPNAME, --setup=SETUPNAME  name of the setup, default is 'watchdog'


Setup file
----------

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
           pausecount = True,
           message = 'Beryllium filter temperature too high',
           gracetime = 0),
      dict(condition = 'shutter_value == "closed"',
           type = '',
           pausecount = True,
           message = 'Instrument shutter is closed',
           gracetime = 0),
      dict(condition = 'reactorpower_value < 15',
           precondtion = 'reactorpower_value > 19',
           precondtime = 600,
           gracetime = 120,
           message = 'reactor power loss',
           pausecount = True),
  ]

  devices = dict(

      mailer   = device('devices.notifiers.Mailer',
                        sender = 'root@demo'),

      smser    = device('devices.notifiers.SMSer',
                        receivers = [...]),

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
   The condition to check.  It typically includes a device
   value, specified as a lowercased cache key with '/' replaced by '_' (so
   ``t_value`` is the value of device ``T``, ``t_setpoint`` is the value of
   the parameter ``T.setpoint`` and so on).  Multiple

   The condition uses Python syntax, so you can use comparison operators (``>``,
   ``>=``, ``==``, ``!=``, ``<=``, ``<``), mathematical operators like ``+``,
   boolean operators (``and`` and ``or``), and group using parentheses.  A
   complex condition might look like this::

     condition = '(ana_value > 1.58 and befilter == "ana") or (mono_value > 1.58 and befilter == "mono")'

**setup**
   If present, the name of a setup that must be loaded in the NICOS master for
   this condition to be active.  By default, the condition is always active.

**gracetime**
   The time, in seconds, which the watchdog waits after a condition becomes true
   until a warning is emitted.  If the condition becomes false again during the
   gracetime, no warning is emitted.  The default gracetime is 5 seconds.

**precondition**
   If present, this condition must be fullfiled for at least ``precondtime``,
   before condition will trigger. Default is no precondition.

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
   "pausecount" is set, see below.

   See :ref:`notifiers` for a list of classes that can be used as notifiers.

**pausecount**
   If this is True, if the condition is detected the NICOS master gets a request
   to pause the count loop, if it is currently in a ``count()`` operation.  If
   not, the master will halt at the beginning of the next count operation.  When
   the condition is back to normal, the operation continues.

   This requires all used detectors to support pause/resume.

**action**
   An action, expressed as NICOS commands, to be executed when the condition is
   detected.  It is run in a separate process, and therefore it can take a few
   seconds until the action is actually executed.  This should not be used for
   very time-critical conditions.
