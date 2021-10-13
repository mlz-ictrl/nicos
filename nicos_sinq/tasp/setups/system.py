description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    datasinks = ['conssink', 'dmnsink', 'livesink', 'illsink'],
    experiment = 'Exp',
)

modules = [
    'nicos.commands.standard',
    'nicos_sinq.commands.sics',
    'nicos_sinq.commands.epicscommands',
]

devices = dict(
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
        sendmail = False,
        serviceexp = 'Service',
        sample = 'Sample',
    ),
    Sample = device('nicos.devices.tas.TASSample',
        description = 'Sample under investigation',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
    illsink = device('nicos_sinq.devices.illasciisink.ILLAsciiSink',
        filenametemplate = ['tasp%(year)sn%(scancounter)06d.dat'],
        scaninfo = ['mon1', 'mon2', 'ctr1', 'elapsedtime', 'protoncount'],
        varia = [
            'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'mcv', 'sro', 'ach', 'mtl',
            'stl', 'stu', 'stl', 'atu', 'mgl', 'sgl', 'sgu', 'agl', 'atl', 'tt',
            'mf', 'tem', 'stick'
        ],
    ),
)
