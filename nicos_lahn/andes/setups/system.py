# A detailed description of the setup file structure and it's elements is
# available here: https://forge.frm2.tum.de/nicos/doc/nicos-stable/setups/
#
# Please remove these lines after copying this file.

description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    # Adapt this name to your instrument's name (also below).
    instrument = 'Andes',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink', 'nxsink'],
#    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

# includes = [
#     'notifiers',
# ]

devices = dict(
    Andes = device('nicos.devices.instrument.Instrument',
        description = 'Advanced Neutron Diffractometer for Engineering and Science',
        instrument = 'ANDES',
        responsible = 'Leonardo J. Ibanez <leonardoibanez@cnea.gob.ar>',
        website = 'http://www.lahn.cnea.gov.ar/index.php/instrumentacion/escaner-de-tensiones-difractometro',
        operators = ['Laboratorio Argentino de Haces de Neutrones'],
        facility = 'LAHN',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),

    # Configure dataroot here (usually /data).
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/mnt/nfs_clientshare/andes/',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    nxsink = device('nicos_sinq.nexus.nexussink.NexusSink',
        description = "sink for NeXus file writer",
        filenametemplate = ['andes%(year)sn%(scancounter)06d.hdf'],
        templateclass = 'nicos_lahn.andes.nexus.nexus_templates.ANDESTemplateProvider',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = '/mnt/nfs_clientshare/andes/',
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
