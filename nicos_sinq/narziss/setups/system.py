description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'NARZISS',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'livesink', 'sinqsink'],
)

modules = [
    'nicos.commands.standard',
    'nicos_sinq.commands.sics',
    'nicos_sinq.commands.epicscommands',
]

devices = dict(
    NARZISS = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ NARZISS',
        responsible = 'Christine Klauser <Christine.Klauser@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        doi = 'http://dx.doi.org/10.1016/j.nima.2011.08.022',
        website = 'https://www.psi.ch/sinq/NARZISS/',
    ),
    Sample = device('nicos.devices.experiment.Sample',
        description = 'The defaultsample',
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
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    sinqsink = device('nicos_sinq.devices.sinqasciisink.SINQAsciiSink',
        filenametemplate = ['narziss%(year)sn%(scancounter)06d.dat'],
        templatefile = 'nicos_sinq/narziss/narziss.hdd',
        scaninfo = [
            ('COUNTS', 'ctr1'), ('MONITOR1', 'mon1'), ('TIME', 'elapsedtime')
        ],
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
)
