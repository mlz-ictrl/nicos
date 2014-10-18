#  -*- coding: utf-8 -*-

description = 'system setup for PUMA'

group = 'lowlevel'

#includes = ['puma']

sysconfig = dict(
    cache = 'pumahw',
    #~ instrument = 'puma',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

devices = dict(
#    puma = device('devices.instrument.Instrument',
#                    instrument = 'PUMA',
#                    responsible = 'O. Sobolev, J. T. Park, A. Teichert',
#                    ),
    Exp      = device('panda.experiment.PandaExperiment',
                      sample = 'Sample',
                      dataroot = '/data',
                      propdb = '/pumacontrol2/propdb',
                      managerights = dict( enableDirMode=0o775,
                                           enableFileMode=0o664,
                                           disableDirMode=0o700,
                                           disableFileMode=0o600,
                                           owner='nicd', group='puma'),
                      sendmail = True,
                      zipdata = True,
                      mailserver = 'smtp.frm2.tum.de',
                      mailsender = 'puma@frm2.tum.de',
                      localcontact = 'O. Sobolev <oleg.sobolev@frm2.tum.de>',
                      serviceexp = 'service',
                      scancounter = 'filecounter', #backwards compatibility
                      ),
    Sample   = device('devices.tas.TASSample'),
    filesink = device('devices.datasinks.AsciiDatafileSink',
                       description = 'metadevice storing the scanfiles',
                       filenametemplate = ['%(proposal)s_%(counter)08d.dat',
                                           '/%(year)d/cycle_%(cycle)s/'
                                           '%(proposal)s_%(counter)08d.dat'],
                     ),
    conssink = device('devices.datasinks.ConsoleSink'),
    daemonsink = device('devices.datasinks.DaemonSink'),
)

startupcode = '''
'''
