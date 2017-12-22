# -*- coding: utf-8 -*-
description = 'system setup for GALAXI '

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'galaxi',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.galaxi.commands']

includes = ['notifiers']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'Default Sample',
    ),

    # Configure dataroot here (usually /data).
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'Galaxi Experiment ',
        dataroot = '/home/jcns/data',
        sample = 'Sample',
        serviceexp = 'service',
        sendmail = False,
        zipdata = False,
        localcontact = 'Ulrich Ruecker <u.ruecker@fz-juelich.de>'
    ),
    galaxi = device('nicos.devices.instrument.Instrument',
        description = 'GALAXI high resolution diffractometer',
        instrument = 'GALAXI',
        facility = 'FZ-Juelich',
        responsible = 'Ulrich Ruecker <u.ruecker@fz-juelich.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-2-109',
        operators = [u'Jülich Centre for Neutron Science (JCNS)'],
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Device storing scanfiles in Ascii output '
        'format.',
        filenametemplate = [
            '%(session.experiment.users)s_%(session.experiment.sample.filename)s_'
            '%(session.experiment.lastscan)s.dat'
        ],
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
