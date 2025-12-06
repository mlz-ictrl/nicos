description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'BOA',
    experiment = 'Exp',
    datasinks = [
        'conssink',
        'dmnsink',
        'nxsink',
    ],
)

modules = [
    'nicos.commands.standard', 'nicos_sinq.commands.sics',
    'nicos_sinq.commands.hmcommands', 'nicos_sinq.commands.epicscommands',
    'nicos_sinq.boa.commands.boasetup'
]

includes = [
    'drot1',
    'drot2',
    'hipa',
    'rotation_ra',
    'table2',
    'table3',
    'table4',
    'table5',
    'table6',
]

devices = dict(
    BOA = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ BOA',
        responsible = 'Patrick Hautle <patrick.hautle@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/BOA/',
    ),
    Sample = device('nicos.devices.experiment.Sample',
        description = 'The defaultsample',
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
    mcu3 = device('nicos_sinq.devices.epics.extensions.EpicsCommandReply',
        description = 'Controller of the devices connected to mcu3',
        commandpv = 'SQ:BOA:turboPmac3.AOUT',
        replypv = 'SQ:BOA:turboPmac3.AINP',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    nxsink = device('nicos.nexus.NexusSink',
        description = "Sink for NeXus file writer",
        filenametemplate = ['boa%(year)sn%(scancounter)06d.hdf'],
        templateclass =
        'nicos_sinq.boa.nexus.nexus_templates.BOATemplateProvider',
    ),
)
