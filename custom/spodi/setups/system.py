#  -*- coding: utf-8 -*-
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
    cache = 'spodictrl.spodi.frm2',
    instrument = 'Spodi',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink', 'spodisink'],
    notifiers = ['email', 'smser'],
)

modules = ['commands.standard']

includes = ['notifiers', ]

# devices: Contains all device definitions.
# A device definition consists of a call like device(classname, parameters).
# The class name is fully qualified (i.e., includes the package/module name).
# The parameters are given as keyword arguments.
devices = dict(
    Spodi = device('devices.instrument.Instrument',
                   description = 'instrument object',
                   instrument = 'SPODI',
                   doi = 'http://dx.doi.org/10.17815/jlsrf-1-24',
                   responsible = 'Markus Hoelzel <markus.hoelzel@frm2.tum.de>',
                   website = 'http://www.mlz-garching.de/spodi',
                   operators = [u'Technische Universität München (TUM)',
                                u'Karlsruher Institut für Technologie (KIT)',
                                ],
                  ),

    Sample   = device('devices.sample.Sample',
                      description = 'The current used sample',
                     ),

    # Configure dataroot here (usually /data).
    Exp      = device('frm2.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/data',
                      propdb = '/spodicontrol/propdb',
                      sendmail = True,
                      serviceexp = 'p0',
                      sample = 'Sample',
                      mailsender = 'spodi@frm2.tum.de',
                      elog = True,
                      managerights = dict(enableDirMode=0o775,
                                          enableFileMode=0o644,
                                          disableDirMode=0o550,
                                          disableFileMode=0o440,
                                          owner='spodi', group='spodi'),
                     ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    daemonsink = device('devices.datasinks.DaemonSink',
                        lowlevel = True,
                       ),
    livesink   = device('devices.datasinks.LiveViewSink',
                        lowlevel = True,
                       ),
    spodisink = device('spodi.datasinks.CaressHistogram',
                       description = 'SPODI specific histogram file format',
                       lowlevel = True,
                       filenametemplate = ['run%(pointcounter)06d.ctxt'],
                       detectors = ['adet'],
                      ),
    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = '/data',
                      minfree = 5,
                     ),
)

display_order = 70
