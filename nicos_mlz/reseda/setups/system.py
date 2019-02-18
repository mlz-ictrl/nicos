#  -*- coding: utf-8 -*-

description = 'system setup'
group = 'lowlevel'
includes = [
    'notifiers',
]

sysconfig = dict(
    cache = 'resedactrl.reseda.frm2',
    instrument = 'reseda',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'slacker'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.reseda.tuning_commands',  'nicos_mlz.reseda.commands']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'The sample',
    ),
    reseda = device('nicos.devices.instrument.Instrument',
        description = 'Resonance spin echo spectrometer',
        instrument = 'RESEDA',
        responsible = 'Christian Franz <christian.franz@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-37',
        website = 'http://www.mlz-garching.de/reseda',
        operators = [u'Technische Universität München (TUM)'],
    ),
    Exp = device('nicos_mlz.reseda.devices.experiment.Experiment',
        description = 'Experiment object',
        dataroot = '/data',
        sendmail = True,
        serviceexp = 'p0',
        sample = 'Sample',
        mailsender = 'reseda@frm2.tum.de',
        propdb = '/resedacontrol/propdb',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    DataSpace = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = '/data',
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = '/resedacontrol/log',
        minfree = 0.5,
        lowlevel = True,
    ),
)
