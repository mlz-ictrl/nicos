#  -*- coding: utf-8 -*-

description = 'system setup'

sysconfig = dict(
    cache = 'antareshw.antares.frm2',
    instrument = 'ANTARES',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.basic', 'nicos.commands.standard', 'nicos.commands.imaging']

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      sender = 'michael.schulz@frm2.tum.de',
                      copies = ['michael.schulz@frm2.tum.de'],
                      subject = 'ANTARES'),

    smser    = device('devices.notifiers.SMSer',
                      receivers = ['015121100909'],
                      server = 'triton.admin.frm2'),

    Sample   = device('devices.experiment.Sample',
                       description = 'Default Sample',
                     ),

    Exp      = device('antares.experiment.Experiment',
                       description = 'Antares Experiment',
                       dataroot = '/data/FRM-II',
                       sample = 'Sample',
                       propdb = '/etc/propdb',
                       localcontact = 'Michael Schulz ' \
                                    '<michael.schulz@frm2.tum.de>',
                       mailsender = 'antares@frm2.tum.de',
                       propprefix = 'p',
                       serviceexp = 'service',
                       servicescript = '',
                       templates = 'templates',
                       sendmail = False,
                       zipdata = False,
                       scancounter = 'filecounter', #backwards compatibility
                       managerights = dict(enableDirMode=0o775,
                                          enableFileMode=0o664,
                                          disableDirMode=0o775,
                                          disableFileMode=0o664,),

                      ),

    ANTARES  = device('devices.instrument.Instrument',
                       description = 'Antares Instrument',
                       instrument='ANTARES',
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                       description = 'Scanfile storing device',
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
)
