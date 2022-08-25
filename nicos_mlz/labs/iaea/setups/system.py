#  -*- coding: utf-8 -*-

description = 'system setup'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'IAEA',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],  # 'email'],
)

modules = ['nicos.commands.basic', 'nicos.commands.standard',
           'nicos_mlz.antares.commands']

includes = []

dataroot = '/data'

devices = dict(
    Sample = device('nicos.devices.experiment.Sample',
        description = 'Default Sample',
    ),
    Exp = device('nicos.devices.experiment.ImagingExperiment',
        description = 'IAEA tomography and radiography demonstration',
        dataroot = dataroot,
        sample = 'Sample',
        mailsender = '',
        propprefix = 'p',
        serviceexp = 'service',
        servicescript = '',
        templates = 'templates',
        sendmail = False,
        zipdata = False,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o555,
            disableFileMode = 0o444,
        ),
    ),
    IAEA = device('nicos.devices.instrument.Instrument',
        description = 'IAEA tomography and radiography demo station',
        instrument = 'IAEA',
        responsible = 'Burkhard Schillinger <burkhard.schillinger@frm2.tum.de>',
        operators = ['Technische Universität München (TUM)'],
        # website = 'http://www.mlz-garching.de/antares',
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
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space in the RootDir',
        path = '/',
        minfree = 5,
    ),
    HomeSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space in the home directory',
        path = '/home/localadmin',
        minfree = 1,
    ),
    DataSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space on the DataStorage',
        path = dataroot,
        minfree = 50,
    ),
    VarSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space on /var',
        path = '/var',
        minfree = 3,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = '/home/localadmin/nicos/log',
        warnlimits = (0.5, None),
    ),
)
