# A detailed description of the setup file structure and it's elements is
# available here: https://forge.frm2.tum.de/nicos/doc/nicos-stable/setups/
#
# Please remove these lines after copying this file.

description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    # Adapt this name to your instrument's name (also below).
    instrument = 'Astor',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink'],
#    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

# includes = [
#     'notifiers',
# ]

devices = dict(
    Astor = device('nicos.devices.instrument.Instrument',
        description = 'Advanced System of Tomography and Radiography',
        instrument = 'ASTOR',
        responsible = 'Leonardo J. Ibanez <leonardoibanez@cnea.gob.ar>',
        website = 'http://www.lahn.cnea.gov.ar/index.php/instrumentacion/tomografo',
        operators = ['Laboratorio Argentino de Haces de Neutrones'],
        facility = 'LAHN',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),

    # Configure dataroot here (usually /data).
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/mnt/nfs_clientshare/astor/',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = '/mnt/nfs_clientshare/astor/',
        warnlimits = (5., None),
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = 'log',
        warnlimits = (.5, None),
        minfree = 0.5,
        lowlevel = True,
    ),
)
