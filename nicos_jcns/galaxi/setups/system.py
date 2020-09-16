# -*- coding: utf-8 -*-

description = 'system setup of the GALAXI diffractometer'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'galaxi',
    experiment = 'Exp',
    datasinks = [
        'conssink', 'daemonsink', 'filesink', 'liveviewsink', 'sampledbsink',
    ],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard', 'nicos_jcns.galaxi.commands']

includes = ['notifiers']

devices = dict(
    Sample = device('nicos_jcns.devices.sample.Sample',
        description = 'GALAXI sample supporting ID validation in the IFF '
        'sample database.',
    ),
    Exp = device('nicos_jcns.devices.experiment.Experiment',
        description = 'GALAXI experiment supporting storage of scan metadata '
        'in the IFF sample database.',
        dataroot = '/home/jcns/data',
        sample = 'Sample',
        serviceexp = 'service',
        sendmail = False,
        zipdata = False,
        localcontact = 'Ulrich Ruecker <u.ruecker@fz-juelich.de>'
    ),
    galaxi = device('nicos.devices.instrument.Instrument',
        description = 'GALAXI high resolution diffractometer.',
        instrument = 'GALAXI',
        facility = 'Forschungszentrum Juelich',
        responsible = 'Ulrich Ruecker <u.ruecker@fz-juelich.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-2-109',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
    ),
    sampledbsink = device('nicos_jcns.devices.sampledbsink.DataSink',
        description = 'Device storing scan metadata in the IFF sample '
        'database.',
        settypes = ['scan', 'subscan'],
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'Device storing console output.',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'Device storing daemon output.',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Device storing scanfiles in Ascii output format.',
        filenametemplate = [
            '%(session.experiment.users)s_'
            '%(session.experiment.sample.filename)s_'
            '%(session.experiment.lastscan)s.dat'
        ],
    ),
    liveviewsink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Device showing live data during measurements.',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
