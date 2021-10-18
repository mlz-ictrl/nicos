#  -*- coding: utf-8 -*-

description = 'system setup for PUMA'

group = 'lowlevel'

sysconfig = dict(
    cache = 'pumadma.puma.frm2',
    instrument = 'puma',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    puma = device('nicos.devices.instrument.Instrument',
        description = 'DAS PUMA',
        instrument = 'PUMA',
        responsible = 'J. T. Park <jitae.park@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-36',
        website = 'http://www.mlz-garching.de/puma',
        operators = [
            'Technische Universität München (TUM)',
            'Institut für Physikalische Chemie, Georg-August-Universität '
            'Göttingen',
        ],
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'Experiment of PUMA',
        sample = 'Sample',
        dataroot = '/data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o600,
            owner = 'nicd',
            group = 'puma'
        ),
        sendmail = True,
        zipdata = True,
        mailserver = 'mailhost.frm2.tum.de',
        mailsender = 'puma@frm2.tum.de',
        serviceexp = 'service',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'Currently used sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = '/control/log',
        lowlevel = True,
        warnlimits = (0.5, None),
    ),
)
