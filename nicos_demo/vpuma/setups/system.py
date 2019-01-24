#  -*- coding: utf-8 -*-

description = 'system setup for PUMA'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'puma',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

devices = dict(
    puma = device('nicos.devices.tas.TAS',
        description = 'Virtual DAS PUMA',
        instrument = 'V-PUMA',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-36',
        website = 'http://www.mlz-garching.de/puma',
        facility = 'NICOS demo instruments',
        operators = ['NICOS developer team'],
        energytransferunit = 'meV',
        scatteringsense = (-1, 1, -1),
        cell = 'Sample',
        phi = 'phi',
        psi = 'sth',
        mono = 'mono',
        ana = 'ana',
        alpha = None,
        axiscoupling = False,
        collimation = '60 30 30 60',
    ),
    Exp = device('nicos_mlz.panda.devices.experiment.PandaExperiment',
        description = 'Experiment of PUMA',
        sample = 'Sample',
        dataroot = 'data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o600,
        ),
        sendmail = True,
        zipdata = True,
        mailserver = 'mailhost.frm2.tum.de',
        mailsender = 'puma@frm2.tum.de',
        serviceexp = 'service',
    ),
    Sample = device('nicos.devices.tas.TASSample',
        description = 'Currently used sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'metadevice storing the scanfiles',
        filenametemplate = [
            '%(proposal)s_'
            '%(scancounter)08d.dat', '/%(year)d/cycle_%(cycle)s/'
            '%(proposal)s_'
            '%(scancounter)08d.dat'
        ],
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'handles console output',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'handles I/O inside daemon',
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = 'log',
        lowlevel = True,
        warnlimits = (0.5, None),
    ),
)
