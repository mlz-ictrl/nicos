#  -*- coding: utf-8 -*-

description = 'system setup'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'NRS',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.basic', 'nicos.commands.standard',
           'nicos_mlz.antares.commands']

devices = dict(
    Sample = device('nicos.devices.experiment.Sample',
        description = 'Default Sample',
    ),
    Exp = device('nicos_inl.nrs.devices.experiment.ImagingExperiment',
        description = 'North radiography station experiment',
        dataroot = '/data/',
        sample = 'Sample',
        mailsender = 'aaron.craft@inl.gov',
        propprefix = '',
        serviceexp = 'service',
        servicescript = '',
        strictservice = True,
        templates = 'templates',
        sendmail = False,
        zipdata = False,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o775,
            disableFileMode = 0o664,
        ),
    ),
    NRS = device('nicos.devices.instrument.Instrument',
        description = 'North radiography station',
        instrument = 'NRS',
        responsible = 'Aaron E. Craft <aaron.craft@inl.gov>',
        operators = ['Idaho National Laboratory'],
        website = 'http://mfc.inl.gov',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Scanfile storing device',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'Device handling console output',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'Data handling inside the daemon',
    ),
    DataSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space on the DataStorage',
        path = '/data',
        minfree = 500,
    ),
)
