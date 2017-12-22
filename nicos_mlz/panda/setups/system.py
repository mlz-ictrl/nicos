#  -*- coding: utf-8 -*-

description = 'system setup for PANDA'

group = 'lowlevel'

sysconfig = dict(
    cache = 'phys.panda.frm2',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
    instrument = 'panda',
    experiment = 'Exp',
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Exp = device('nicos_mlz.panda.devices.experiment.PandaExperiment',
        description = 'Experiment device for Panda',
        sample = 'Sample',
        dataroot = '/data',
        templates = 'templates',
        propdb = '/usr/local/nicos/nicos_mlz/panda/setups/special/propdb',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o600,
            owner = 'jcns',
            group = 'panda'
        ),
        sendmail = True,
        zipdata = True,
        mailserver = 'mailhost.frm2.tum.de',
        mailsender = 'panda@frm2.tum.de',
        serviceexp = 'service',
    ),
    panda = device('nicos.devices.instrument.Instrument',
        description = 'the PANDA spectrometer',
        instrument = 'PANDA',
        responsible = 'Astrid Schneidewind <astrid.schneidewind@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-35',
        operators = [u'Jülich Centre for Neutron Science (JCNS)'],
        website = 'http://www.mlz-garching.de/panda',
    ),
    Sample = device('nicos.devices.tas.TASSample',
        description = 'Sample under investigation',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'metadevice storing the scanfiles',
        filenametemplate = [
            '%(proposal)s_%(scancounter)08d.dat',
            '/%(year)d/links/%(proposal)s_%(scancounter)08d.dat',
        ],
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'device used for console-output',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'device used for output from the daemon',
    ),
)
