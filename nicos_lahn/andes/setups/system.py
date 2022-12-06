description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    # Adapt this name to your instrument's name (also below).
    instrument = 'ANDES',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink', 'nxsink'],#'rawsink', 'nxsink'],
    #notifiers = [],  # ['email'],
)

modules = ['nicos.commands.standard']

includes = [
#    'notifiers',
]

devices = dict(
    ANDES = device('nicos.devices.instrument.Instrument',
        description = 'Advanced Neutron Diffractometer for Engineering and Science',
        instrument = 'ANDES',
        responsible = 'Dr. Miguel A. Vicente" <m.a.vicente@cab.cnea.gov.ar>',
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
        dataroot = '/mnt/nfs/andes/data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
        forcescandata = True,
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    #rawsink = device ('nicos.devices.datasinks.RawImageSink'),
    nxsink = device('nicos.nexus.NexusSink',
        templateclass = 'nicos_lahn.andes.nexus.nexus_templates.ANDESTemplateProvider',
        filenametemplate = ['%(proposal)s_%(scancounter)08d.hdf'],
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = '/mnt/nfs',
        warnlimits = (5., None),
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = None,
        warnlimits = (.5, None),
        minfree = 0.5,
        visibility = ('devlist',),
    ),
)
