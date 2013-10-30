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
                      managerights = True,
                      sendmail = True,
                      zipdata = True,
                      mailserver = 'smtp.frm2.tum.de',
                      mailsender = 'puma@frm2.tum.de',
                      serviceexp = 'service',
                      reporttemplate = 'experimental_report.rtf',
                      ),
    Sample   = device('devices.tas.TASSample'),
    filesink = device('devices.datasinks.AsciiDatafileSink',
                      globalcounter = '/data/filecounter'),
    conssink = device('devices.datasinks.ConsoleSink'),
#    liveplot = device('nicos.data.GraceSink'),
    daemonsink = device('devices.datasinks.DaemonSink'),
)

startupcode = '''
'''
