description = 'system setup'

group = 'lowlevel'

display_order = 90

sysconfig = dict(
    cache = 'localhost',
    instrument = 'NEUTRA',
    experiment = 'Exp',
    datasinks = [
        'conssink', 'dmnsink', 'livesink', 'asciisink'
        #, 'shuttersink'
    ],
    notifiers = ['email'],
)

includes = ['shutters']

modules = [
    'nicos.commands.standard', 'nicos_sinq.commands.sics',
    'nicos.commands.imaging', 'nicos_sinq.commands.hmcommands',
    'nicos_sinq.commands.epicscommands'
]

includes = ['notifiers']

devices = dict(
    NEUTRA = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ NEUTRA',
        responsible = 'Pavel Trtik <pavel.trtik@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        doi = 'http://dx.doi.org/10.1080/10589750108953075',
        website = 'https://www.psi.ch/sinq/NEUTRA/',
    ),
    Sample = device('nicos.devices.experiment.Sample',
        description = 'The defaultsample',
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
    asciisink = device('nicos.devices.datasinks.AsciiScanfileSink',
        filenametemplate = ['neutra%(year)sn%(scancounter)06d.dat']
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
    img_index = device('nicos.devices.generic.manual.ManualMove',
        description = 'Keeps the index of the last measured image',
        unit = '',
        abslimits = (0, 1e9),
        visibility = set(),
    ),
    proton_current = device('nicos.devices.epics.pva.EpicsReadable',
        description = 'Proton current from HIPA',
        readpv = "MHC6:IST:2",
        monitor = True,
    ),
)
