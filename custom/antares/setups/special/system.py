#  -*- coding: utf-8 -*-

description = 'system setup'

sysconfig = dict(
    cache = 'antareshw.antares.frm2',
    instrument = 'ANTARES',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard', 'antares.commands']

devices = dict(
    Sample   = device('devices.experiment.Sample',
                       description = 'Default Sample',
                     ),

    Exp      = device('antares.experiment.Experiment',
                       description = 'Antares Experiment',
                       dataroot = '/data/FRM-II',
                       sample = 'Sample',
                       propdb = '/etc/propdb',
                       localcontact = 'Michael Schulz',
                       mailsender = 'antares@frm2.tum.de',
                       propprefix = 'p',
                       serviceexp = 'service',
                       servicescript = 'start_service.py',
                       templatedir = 'templates',
                       managerights = True,
                       sendmail = False,
                       zipdata = False,
                      ),

    ANTARES  = device('devices.instrument.Instrument',
                       description = 'Antares Instrument',
                       instrument='ANTARES',
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                       description = 'Scanfile storing device',
                       globalcounter = '/data/FRM-II/filecounter',
                     ),

    conssink = device('devices.datasinks.ConsoleSink',
                       description = 'Device handling console output',
                     ),

    daemonsink = device('devices.datasinks.DaemonSink',
                         description = 'Data handling inside the daemon',
                        ),

    Space     = device('devices.generic.FreeSpace',
                        description = 'Free Space in the RootDir of AntaresHW',
                        path = '/',
                        minfree = 5,
                      ),

    DataSpace = device('devices.generic.FreeSpace',
                        description = 'Free Space on the DataStorage',
                        path = '/data',
                        minfree = 500,
                      ),

#    UBahn     = device('frm2.ubahn.UBahn'),
)
