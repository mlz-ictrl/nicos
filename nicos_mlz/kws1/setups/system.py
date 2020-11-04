# -*- coding: utf-8 -*-

description = 'system setup'
group = 'lowlevel'
display_order = 80

sysconfig = dict(
    cache = 'localhost',
    instrument = 'KWS1',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

includes = ['notifiers']

modules = ['nicos.commands.standard']

devices = dict(
    KWS1 = device('nicos.devices.instrument.Instrument',
        description = 'KWS-1 instrument',
        instrument = 'KWS-1',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-26',
        responsible = 'H. Frielinghaus <h.frielinghaus@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
        website = 'http://www.mlz-garching.de/kws-1',
    ),
    Sample = device('nicos_mlz.kws1.devices.sample.KWSSample',
        description = 'Sample object',
    ),
    Exp = device('nicos_mlz.kws1.devices.experiment.KWSExperiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = True,
        mailsender = 'kws1@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        serviceexp = 'maintenance',
        sample = 'Sample',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o500,
            disableFileMode = 0o400,
            owner = 'jcns',
            group = 'games'
        ),
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    UBahn = device('nicos_mlz.devices.ubahn.UBahn',
        description = 'Next departures of the U-Bahn from station '
                      'Garching-Forschungszentrum to Munich',
        fmtstr='%s',
    ),
    OutsideTemp = device('nicos.devices.tango.Sensor',
        description = 'Outdoor air temperature',
        tangodevice = 'tango://ictrlfs.ictrl.frm2:10000/frm2/meteo/temp',
    ),
)

extended = dict(
    representative = 'Sample',
)
