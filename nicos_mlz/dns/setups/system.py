#  -*- coding: utf-8 -*-
description = 'system setup for DNS '

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'dns',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'Default Sample',
    ),

    # Configure dataroot here (usually /data).
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'Dns Experiment ',
        dataroot = '/data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o750,
            disableFileMode = 0o440,
            enableOwner = 'jcns',
            enableGroup = 'games',
            disableOwner = 'jcns',
            disableGroup = 'dns',
        ),
        sample = 'Sample',
        propprefix = 'p',
        serviceexp = 'service',
        sendmail = False,
    ),
    dns = device('nicos.devices.instrument.Instrument',
        description = 'DNS Diffuse scattering neutron ' +
        'time of flight spectrometer',
        instrument = 'DNS',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-33',
        responsible = 'Yixi Su <y.su@fz-juelich.de>',
        website = 'http://www.mlz-garching.de/dns',
        operators = [u'Jülich Center for Neutron Science (JCNS)'],
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Device storing scanfiles in Ascii output format.',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'Device storing console output.',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'Device storing deamon output.',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
