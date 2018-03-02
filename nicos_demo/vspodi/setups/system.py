#  -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Spodi',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'spodilivesink',
        'spodisink',
    ],
    # notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

# includes = ['notifiers']

# devices: Contains all device definitions.
# A device definition consists of a call like device(classname, parameters).
# The class name is fully qualified (i.e., includes the package/module name).
# The parameters are given as keyword arguments.
devices = dict(
    Spodi = device('nicos.devices.instrument.Instrument',
        description = 'Virtual SPODI instrument',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        instrument = 'V-SPODI',
        website = 'http://www.mlz-garching.de/spodi',
        operators = ['NICOS developer team'],
        facility = 'NICOS demo instruments',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-24',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'p0',
        sample = 'Sample',
        reporttemplate = '',
        elog = True,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
            # owner = 'spodi',
            # group = 'spodi'
        ),
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The current used sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        lowlevel = True,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        lowlevel = True,
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        lowlevel = True,
    ),
    spodisink = device('nicos_mlz.spodi.devices.datasinks.CaressHistogram',
        description = 'SPODI specific histogram file format',
        lowlevel = True,
        filenametemplate = ['m1%(pointcounter)08d.ctxt'],
        detectors = ['adet'],
    ),
    spodilivesink = device('nicos_mlz.spodi.devices.datasinks.LiveViewSink',
        lowlevel=True,
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = 'data',
        minfree = 5,
    ),
)
