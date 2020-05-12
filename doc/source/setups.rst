.. _setups:

Configuring NICOS: Setups
=========================

-----------
Setup files
-----------

NICOS supports the concept of different instrument setups.  Not all devices that
can be used at an instrument will be present all the time, so they need not be
loaded.

A specific set of devices (and commands, which supports the notion of
specialized commands) is collected in a "setup file"[#f1]_.

The syntax of the setup files is python-like.

Each setup is available by the filename without the '.py' extension, e.g. the
'test' setup is located in 'test.py' file.  Setup names may contain ASCII
letters, numbers, the underscore and the minus sign.

A setup named ``system``, if it exists, is **always** loaded by NICOS.

A setup file can consist of the following entries, all of which are optional
except the :ref:`description <setup-description>` entry:

* :ref:`description <setup-description>`
* :ref:`group <setup-group>`
* :ref:`includes <setup-includes>`
* :ref:`excludes <setup-excludes>`
* :ref:`sysconfig <setup-sysconfig>`
* :ref:`devices <setup-devices>`
* :ref:`modules <setup-modules>`
* :ref:`startupcode <setup-startupcode>`
* :ref:`display_order <setup-display_order>`
* :ref:`alias_config <setup-alias_config>`
* :ref:`monitor_blocks <setup-monitor_blocks>`
* :ref:`watch_conditions <setup-watch_conditions>`
* :ref:`extended <setup-extended>`

.. _setup-description:

``description``
   A string describing the setup in detail. The entry will be displayed to the
   user in client interfaces, if the setup is not in one of the following
   :ref:`groups <setup-group>`:

   * ``'lowlevel'``
   * ``'special'``
   * ``'configdata'``

   Example::

      description = 'triple-axis measurement setup'

.. note::

   It's a good pratice to add the description to every setup file and device.

.. _setup-group:

``group``
   A string giving the group of the setup.  The following groups are
   recognized:

   * ``basic`` means a basic setup for the instrument, of which only one should
     be loaded (e.g. "twoaxis" or "threeaxis").  These setups can be presented
     to the user.
   * ``optional`` means an optional setup, of which as many as needed can be
     loaded.  These setups can be presented to the user for multiple selection.
     This is the default.
   * ``plugplay`` means an optional setup that is automatically detected by
     NICOS when the corresponding hardware (usually sample environment) is
     present.
   * ``lowlevel`` means a low-level setup, which will be included by others,
     but should not be presented to users.

   * ``configdata`` means that the setup does not contain devices or includes,
     but only configuration data (in the form of lists, dictionaries, etc).  See
     :ref:`config-setups` below.

   * ``special`` means that the setup is not a setup of instrument devices,
     but configures e.g. a NICOS service.  For each service, there is one
     special setup (e.g. "cache", "poller", "daemon").

   Example::

      group = 'optional'

.. _setup-includes:

``includes``
   A list of names of setups that this one requires to be loaded.  Using this
   function, setups can be constructed very modularly, usually without
   duplicating the entry for any device.

   Example::

      includes = ['base', 'mono1', 'sample', 'detector']

.. _setup-excludes:

``excludes``
   A list of names of setups that must **not** be loaded if this setup file
   should be loaded. If one of this is loaded and you try to load this file,
   an error message will be generated.

   Possible uses of this directive:

   - setups which contain the same device in different configurations
   - setups that would disturb the current setup when loaded

   Example::

      excludes = ['eulerian_huber', 'eulerian_newport']

.. _setup-sysconfig:

``sysconfig``
   A dictionary with basic system configuration values.  Most values are usually
   only put in one very basic setup file that is included from other, more
   high-level files.

   Example::

       sysconfig = dict(
           cache = 'mira1',
           instrument = 'mira',
           experiment = 'Exp',
           notifiers = ['email', 'smser'],
           datasinks = ['conssink', 'filesink', 'dmnsink'],
       )

   The possible entries are:

   `cache`
      A string giving the ``hostname`` of the cache server (or ``hostname:port``,
      if the cache runs on a port other than 14869).  If this is omitted, no
      caching will be available.

      See also :ref:`cache`.

   `instrument`
      The name of the instrument device, defined somewhere in a ``devices``
      dictionary.  The class for this device **must** be
      :class:`nicos.devices.instrument.Instrument` or an instrument-specific
      subclass.

   `experiment`
      ``'Exp'`` or ``None``.  If ``'Exp'``, a device of this name must be defined
      somewhere in a ``devices`` dictionary.  The class for this device **must**
      be :class:`nicos.devices.experiment.Experiment` or an instrument-specific
      subclass.

   `datasinks`
      A list of names of :ref:`data-sinks`, i.e. special devices that process
      measured data.  These devices *must* be defined somewhere in a ``devices``
      dictionary.

      A data sink can represent a data storage device, writing the measured data
      in a given format, to be read by data analysis software.

      Other types of data sinks can be used to forward the measured data to other
      components of NICOS (for display purposes) or enter metadata into a catalog.

      Datasinks lists from different loaded setups are merged.

   `notifiers`

      A list of names of "notifiers", i.e. special devices that can notify the
      user or instrument responsibles via various channels (e.g. email).  These
      devices *must* be defined somewhere in a ``devices`` dictionary and be of
      class :class:`nicos.devices.notifiers.Notifier` or a subclass.

      Notifiers lists from different loaded setups are merged.

.. _setup-devices:

``devices``
   A dictionary of devices, where the key is the device name and the value is a
   device definition.

   A device definition consists of a call like ``device(classname, parameters)``.
   The class name is fully qualified (i.e., includes the package/module name).
   See the :doc:`class documentation <classes/index>` for the existing device
   classes.  The parameters are given as keyword arguments.  Here are some
   example ``devices`` entries::

      devices = dict(
          p   = device('nicos.devices.taco.AnalogInput',
                       description = 'detector gas pressure',
                       tacodevice = 'mira/ccr/pressure',
                       unit = 'bar'),

          mth_motor = device('nicos.devices.taco.Motor',
                             tacodevice = 'mira/motor/mth',
                             lowlevel = True,
                             unit = 'deg'),

          mth_coder = device('nicos.devices.taco.Coder',
                             tacodevice = 'mira/coder/mth',
                             lowlevel = True,
                             unit = 'deg'),

          mth = device('nicos.devices.generic.Axis',
                       description = 'Monochromator theta angle',
                       motor = 'mth_motor',
                       coder = 'mth_coder',
                       abslimits = (0, 100),
                       userlimits = (0, 50),
                       precision = 0.01),
      )

   For example, an instrument with varying sample environment could have two
   setup files, ``cryostat`` and ``oven``, where both include a ``base`` file
   that could contain the monochromator, sample table and detector that always
   stay the same.

   On startup, an empty setup is initialized by NICOS.  The user then loads a
   setup using the ``NewSetup('modulename')`` command.  Each time the
   ``NewSetup`` command is used, the previous setup is unloaded and the created
   devices are destroyed.  When more setups need to be loaded at the same time,
   the ``AddSetup('modulename')`` command can be used.

.. _setup-modules:

``modules``
   A list of Python module names where additional user commands are loaded from.

   Example::

      modules = ['nicos.commands.standard', 'nicos.commands.utility']

.. _setup-display_order:

``display_order``
   An integer (range 0-100) that determines how the list of loaded setups is
   sorted when displayed in the GUI device list.

   The default is 50.  To sort a setup before the default, use smaller numbers,
   to sort them after the default, use larger numbers.  Setups with the same
   number are sorted alphabetically by setup name.

   Example::

      display_order = 20

.. _setup-alias_config:

``alias_config``
   A dictionary of device aliases that the current setup would like to change.

   This is preferred to setting aliases in the ``startupcode`` since NICOS will
   combine this information from loaded setups and can make decisions how to set
   the aliases.

   The format is the following::

       alias_config = {
           'T':  {'T_ccr12':   100},
           'Ts': {'T_ccr12_A': 100, 'T_ccr12_B':  50},
       }

   It maps the name of the alias device (which must exist in the setup) to a
   dictionary of the desired alias targets and the priority to use them.
   If multiple loaded setups want to change the same alias, the target with
   the highest priority is selected.

   Regarding the choice of the priority numbers:

   - below 0: fallbacks (should normally not be used, but sometimes a (virtual
     dummy fallback) device is needed
   - around 0: instrument default (normally always there, fallback)
   - around 100: 'outermost' optional stuff (magnets, ovens, ...)
   - around 200: 'spezialised' optional stuff (carrying cryostats, extra
     rotational stages)
   - around 300: 'innermost' optional stuff (cci3he/4he inserts, cold-end-sample
     rotation,...)

   If more than one choice is offered by a setupfile, they should have different
   priorities (with the less common/sensible option getting a smaller number).

.. _setup-monitor_blocks:

``monitor_blocks``
   A dictionary of "monitor blocks", i.e. status monitor ``Block()``
   declarations (see :ref:`monitor-elements`) that you want to predefine
   for this setup.

   In a status monitor setup, you can then use these predefined blocks using
   ``SetupBlock('setupname')`` or ``SetupBlock('setupname', 'blockname')``.
   The *blockname* is the key into this dictionary, and if not given, is
   ``'default'``.

   Blocks defined like this should normally have the ``setups`` parameter
   set to ``setupname``, so that the block is only shown when the setup is
   loaded.

   Example, in a setup "cryo1"::

      monitor_blocks = {
          'default': Block('Cryostat 1', [
                         BlockRow('T_cryo1', 'T_cryo1_sample'),
                         BlockRow('p_cryo1')
                     ], setups=setupname)
      }

.. _setup-watch_conditions:

``watch_conditions``
   A list of watch conditions that should be used by the watchdog service
   if this setup is loaded.

   The format of these conditions is explained in :ref:`watch-conditions`.

   Example::

      watch_conditions = [
          dict(condition = 't_value > 300',
               message = 'Temperature too high (exceeds 300 K)',
               type = 'critical',
               gracetime = 10,
              ),
      ]

.. _setup-startupcode:

``startupcode``
   A string of Python code that is executed after the setup file has been
   processed and the devices that are marked for automatic creation have been
   created.

   Example::

      startupcode = '''
      AddEnvironment(T, Ts)
      '''

.. _setup-extended:

``extended``
   A dictionary, reserved for future use.

   Example::

      extended = dict(dynamic_loaded = True)

.. todo::

   document "extended" more once we have use for it. PANDA uses it now !!!


.. _config-setups:

--------------------
Configuration setups
--------------------

The setup kind ``configdata`` marks setups that do not contain devices,
includes, startupcode etc., but arbitrary configuration data (in the form of
Python lists, dictionaries, etc) that is used by other setups.  This is helpful
if this data is autogenerated, or generated by a GUI tool.  It is also helpful
when the data is used by devices in multiple setups, to avoid duplication.

The setup cannot be loaded as usual, but its data can be included in other
setups using the ``configdata()`` function that is provided when setups are
read.

.. function:: configdata(value)

   This function is available in setups and returns a value from a configuration
   setup.  The argument must be ``'setupname.valuename'``.

   It is typically used like this::

      # setup file "config_det.py"

      group = 'configdata'
      DET_CONFIG = {
          ...  # some configuration data
      }

      # setup file "det.py"

      group = 'lowlevel'

      devices = dict(
          det = device('my.instrument.Detector',
                       # here the DET_CONFIG dictionary is loaded from
                       # config_det.py and inserted as a parameter
                       config = configdata('config_det.DET_CONFIG'),
                       # other parameters...
                      ),
      )

.. rubric:: Footnotes

.. [#f1] A Python module in the subdirectory ``setups`` of the site-specific
         NICOS root directory.
