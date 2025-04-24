description = 'system setup'

group = 'lowlevel'

display_order = 10

sysconfig = dict(
    cache = 'localhost',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'livesink', 'quiecksink', 'nxsink'],
)

modules = [
    'nicos.commands.standard',
    'nicos_sinq.commands.sics',
    'nicos_sinq.commands.hmcommands',
    'nicos_sinq.commands.epicscommands',
    'nicos_sinq.camea.commands.camea',
    'nicos.commands.tas',
    'nicos_sinq.sxtal.commands'
]

devices = dict(
    ublist = device('nicos_sinq.sxtal.reflist.ReflexList',
        description = 'Reflection list for '
        'UB matrix refinement',
        reflection_list = [],
        column_headers = (
            ('H', 'K', 'L', 'EN'), ('A3', 'A4', 'SGU', 'SGL'), ('EI', 'EF')
        ),
    ),
    Sample = device('nicos_sinq.sxtal.sample.SXTalSample',
        description = 'The currently used sample',
        reflists = [
            'ublist',
        ],
        ubmatrix = [1, 0, 0, 0, 1, 0, 0, 0, 1],
        reflist = 'ublist',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
        serviceexp = 'Service',
        sample = 'Sample',
        forcescandata = True,
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sink for forwarding live data to the GUI',
    ),
    nxsink = device('nicos.nexus.NexusSink',
        description = 'Sink for NeXus file writer',
        filenametemplate = ['camea%(year)sn%(scancounter)06d.hdf'],
        templateclass = 'nicos_sinq.camea.nexus.nexus_templates'
        '.CameaTemplateProvider',
    ),
    quiecksink = device('nicos_sinq.devices.datasinks.QuieckSink',
        description = 'Sink for sending UDP datafile notifications',
    ),
)
