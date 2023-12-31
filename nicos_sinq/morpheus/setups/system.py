description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'MORPHEUS',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'livesink', 'sinqsink', 'cclsink'],
)

modules = [
    'nicos.commands.standard', 'nicos_sinq.commands.sics',
    'nicos_sinq.commands.epicscommands', 'nicos_sinq.sxtal.commands'
]

devices = dict(
    MORPHEUS = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ MORPHEUS',
        responsible = 'Jochen Stahn <Jochen.Stahn@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        doi = 'http://dx.doi.org/10.1016/j.nima.2011.08.022',
        website = 'https://www.psi.ch/sinq/MORPHEUS/',
    ),
    Sample = device('nicos.devices.experiment.Sample',
        description = 'NICOS sample object',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
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
        filenametemplate = ['morpheus%(year)sn%(scancounter)06d.dat'],
        templatefile = 'nicos_sinq/morpheus/morpheus.hdd',
        scaninfo = [
            ('COUNTS', 'ctr1'),
            ('MONITOR1', 'mon1'),
            ('TIME', 'elapsedtime'),  #('SPIN', 'spin')
        ],
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
    cclsink = device('nicos_sinq.sxtal.datasink.CCLSink',
        description = 'Sink for writing SINQ ASCII files',
        filenametemplate = ['morpheus%(year)sn%(scancounter)06d.ccl'],
        templatefile = 'nicos_sinq/morpheus/mess.hdd',
        detector = 'ctr1',
        scaninfo = [
            ('COUNTS', 'ctr1'),
            ('MONITOR1', 'mon1'),
            ('TIME', 'elapsedtime'),  #('SPIN', 'spin')
        ]
    ),
)
