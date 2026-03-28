description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'SINQTEST',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'livesink'],
)

modules = [
    'nicos.commands.standard',
    'nicos_sinq.commands.sics',
    'nicos_sinq.commands.epicscommands',
]

devices = dict(
    SINQTEST = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQTEST',
        responsible = 'Mark Koennecke <Mark.Koennecke@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
    ),
    Sample = device('nicos.devices.experiment.Sample',
        description = 'The defaultsample',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
        sample = 'Sample',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    sinqsink = device('nicos_sinq.devices.sinqasciisink.SINQAsciiSink',
        filenametemplate = ['sinqtest%(year)sn%(scancounter)06d.dat'],
        templatefile = 'nicos_sinq/sinqtest/sinqtest.hdd',
        scaninfo = [
            ('COUNTS', 'ctr1'), ('MONITOR1', 'mon1'), ('TIME', 'elapsedtime')
        ],
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
)
