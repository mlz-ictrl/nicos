# description: Description of the setup (detailed)
description = 'system setup'

# group: Group of the setup. The following groups are recognized:
# - basic
#       Basic setup for the instrument, of which only one should be
#       loaded (e.g. "twoaxis" or "threeaxis"). These setups can be
#       presented to the user.
# - optional
#       Optional setup, of which as many as needed can be loaded.
#       These setups can be presented to the user for multiple
#       selection. This is the default.
# - lowlevel
#       Low-level setup, which will be included by others, but should
#       not be presented to users.
# - special
#       The setup is not a setup of instrument devices, but configures
#       e.g. a NICOS service. For each service, there is one special
#       setup (e.g. "cache", "poller", "daemon").
group = 'lowlevel'

# sysconfig: A dictionary with basic system configuration values.
# Possible values:
#   - cache
#       A string giving the hostname[:port] of the cache server,
#       the default port is 14869.
#       If this value is omitted, no caching will be available.
#   - instrument
#       The name of the instrument device, defined somewhere in a
#       devices dictionary. The class for this device must be
#       'nicos.devices.instrument.Instrument' or an instrument-specific
#       subclass.
#   - experiment
#       The name of the experiment "device", defined somewhere in a
#       devices dictionary. The class for this device must be
#       'nicos.devices.experiment.Experiment' or an instrument-specific
#       subclass.
#   - datasinks
#       A list of names of "data sinks", i.e. special devices that
#       process measured data. These devices must be defined somewhere
#       in a devices dictionary and be of class
#       'nicos.devices.datasinks.DataSink' or a subclass.
#   - notifiers
#       A list of names of "notifiers", i.e. special devices that can
#       notify the user or instrument responsibles via various channels
#       (e.g. email). These devices must be defined somewhere in a
#       devices dictionary and be of class
#       'nicos.devices.notifiers.Notifier' or a subclass.

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
#    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

#includes = ['notifiers']

# devices: Contains all device definitions.
# A device definition consists of a call like device(classname, parameters).
# The class name is fully qualified (i.e., includes the package/module name).
# The parameters are given as keyword arguments.
devices = dict(
    V20 = device('nicos.devices.instrument.Instrument',
                      description = 'instrument object',
                      instrument = 'V20',
                      responsible = 'Robin Woracek <robin.woracek@esss.se>',
                      facility='Helmholtz Zentrum Berlin',
                      website='https://www.helmholtz-berlin.de/pubbin/igama_output?' \
                              'modus=einzel&sprache=de&gid=1845&typoid=50726'
                     ),

    Sample   = device('nicos.devices.sample.Sample',
                      description = 'The current used sample',
                     ),

    # Configure dataroot here (usually /data).
    Exp      = device('nicos.devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/home/pi/nicos-core/data',
                      sendmail = True,
                      serviceexp = 'p0',
                      sample = 'Sample',
                     ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    daemonsink = device('nicos.devices.datasinks.DaemonSink',
                        lowlevel = True,
                       ),

    Space    = device('nicos.devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = '/home/pi/nicos-core/data',
                      minfree = 5,
                     ),
)
