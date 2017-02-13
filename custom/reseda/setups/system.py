#  -*- coding: utf-8 -*-

description = 'system setup'
group = 'lowlevel'
includes = [
    'notifiers',
]

sysconfig = dict(
    cache = 'resedahw2.reseda.frm2',
    instrument = 'reseda',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['commands.standard']

devices = dict(
    Sample = device('devices.sample.Sample',
        description = 'The sample',
    ),
    reseda = device('devices.instrument.Instrument',
        description = 'Resonance spin echo spectrometer',
        instrument = 'RESEDA',
        responsible = 'Christian Franz '
        '<christian.franz@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-37',
        website = 'http://mlz-garching.de/instrumente-und-labore/spektroskopie/reseda.html',
    ),
    Exp = device('frm2.experiment.Experiment',
        description = 'Experiment object',
        dataroot = '/data',
        sendmail = True,
        serviceexp = 'p0',
        sample = 'Sample',
        mailsender = 'reseda@frm2.tum.de',
        propdb = '/etc/proposaldb',
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
    DataSpace = device('devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = '/data',
        minfree = 5,
    ),
)
