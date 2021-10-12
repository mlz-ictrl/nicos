description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'ORION',
    experiment = 'Exp',
    datasinks = [
        'conssink', 'dmnsink', 'livesink', 'quiecksink', 'asciisink', 'cclsink'
    ],
)

modules = [
    'nicos.commands.standard', 'nicos_sinq.commands.sics',
    'nicos_sinq.commands.epicscommands', 'nicos_sinq.commands.tableexe',
    'nicos_sinq.sxtal.commands'
]

devices = dict(
    mess = device('nicos_sinq.sxtal.reflist.ReflexList',
        description = 'Reflection list for measurements',
        reflection_list = []
    ),
    ublist = device('nicos_sinq.sxtal.reflist.ReflexList',
        description = 'Reflection list for '
        'UB matrix refinement',
        reflection_list = []
    ),
    Sample = device('nicos_sinq.sxtal.sample.SXTalSample',
        description = 'The currently used sample',
        ubmatrix = [
            -0.0550909, 0.04027, -0.075288, 0.0335794, 0.0925995, 0.0249626,
            0.0785034, -0.0113463, -0.0635126
        ],
        a = 9.8412,
        reflists = ['ublist', 'mess'],
        reflist = 'ublist',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
        sendmail = False,
        serviceexp = 'Service',
        sample = 'Sample',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink', lowlevel = True
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink', lowlevel = True),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sink for forwarding live data to the GUI',
    ),
    quiecksink = device('nicos_sinq.devices.datasinks.QuieckSink',
        description = 'Sink for sending UDP datafile '
        'notifications'
    ),
    asciisink = device('nicos_sinq.sxtal.datasink.SxtalScanSink',
        description = 'Sink for writing SINQ ASCII files',
        filenametemplate = ['orion%(year)sn%(scancounter)06d.dat'],
        templatefile = 'nicos_sinq/orion/orion.hdd',
        lowlevel = True,
        scaninfo = [
            ('COUNTS', 'counts'), ('MONITOR1', 'monitor1'),
            ('TIME', 'elapsedtime')
        ]
    ),
    cclsink = device('nicos_sinq.sxtal.datasink.CCLSink',
        description = 'Sink for writing SINQ ASCII files',
        filenametemplate = ['orion%(year)sn%(scancounter)06d.ccl'],
        templatefile = 'nicos_sinq/orion/mess.hdd',
        lowlevel = True,
        detector = 'counts',
        scaninfo = [
            ('COUNTS', 'counts'), ('MONITOR1', 'monitor1'),
            ('TIME', 'elapsedtime')
        ]
    ),
)
