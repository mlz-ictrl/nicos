# -*- coding: utf-8 -*-

description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'spheres',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.spheres.commands',
           'nicos_mlz.spheres.scan']

includes = ['notifiers']

devices = dict(
    spheres = device('nicos.devices.instrument.Instrument',
        description = 'SPHERES instrument object',
        instrument = 'SPHERES',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-38',
        responsible = 'Michaela Zamponi <m.zamponi@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
        website = 'http://www.mlz-garching.de/spheres',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data/nicos',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
                      subdir='ascii'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
