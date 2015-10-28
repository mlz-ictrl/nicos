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
#        The setup is not a setup of instrument devices, but configures
#        e.g. a NICOS service. For each service, there is one special
#        setup (e.g. "cache", "poller", "daemon").
group = 'lowlevel'

# sysconfig: A dictionary with basic system configuration values.
# Possible values:
#   - cache
#       A string giving the hostname of the cache server (or
#       hostname:port, if the cache runs on a port other than 14869).
#       If this is omitted, no caching will be available.
#   - instrument
#       The name of the instrument device, defined somewhere in a
#       devices dictionary. The class for this device must be
#       'devices.instrument.Instrument' or an instrument-specific
#       subclass.
#   - experiment
#       The name of the experiment "device", defined somewhere in a
#       devices dictionary. The class for this device must be
#       'devices.experiment.Experiment' or an instrument-specific
#       subclass.
#   - datasinks
#       A list of names of "data sinks", i.e. special devices that
#       process measured data. These devices must be defined somewhere
#       in a devices dictionary and be of class
#       'devices.datasinks.DataSink' or a subclass.
#   - notifiers
#       A list of names of "notifiers", i.e. special devices that can
#       notify the user or instrument responsibles via various channels
#       (e.g. email). These devices must be defined somewhere in a
#       devices dictionary and be of class
#       'devices.notifiers.Notifier' or a subclass.

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = [],
    notifiers = ['email'],
)

includes = ['notifiers', ]

modules = ['commands.standard']

# devices: Contains all device definitions.
# A device definition consists of a call like device(classname, parameters).
# The class name is fully qualified (i.e., includes the package/module name).
# The parameters are given as keyword arguments.
devices = dict(
    Sample   = device('devices.sample.Sample',
                      description = 'currently used sample',
                     ),

    # Configure dataroot here (usually /data).
    Exp      = device('devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = 'data',
                      sendmail = True,
                      serviceexp = '0',
                      sample = 'Sample',
                     ),
)
