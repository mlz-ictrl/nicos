description = 'system setup'

display_order = 18

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Amor',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'FileWriterControl'],
)

# Commented out on 27.11.2024 (Stefan Mathis). To be checked in shutdown - is this ever needed?
#  'nicos_ess.commands.filewriter',
modules = [
    'nicos.commands.standard',
    'nicos_sinq.amor.commands',
    'nicos_sinq.commands.sics',
    'nicos_sinq.commands.epicscommands',
]

includes = ['sample']

devices = dict(
    Amor = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ AMOR',
        responsible = 'Jochen Stahn <jochen.stahn@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/amor/amor'
    ),
    Sample = device('nicos_sinq.amor.devices.sample.AmorSample',
        description = 'The currently used sample',
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
        visibility = (),
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    FileWriterStatus = device('nicos_ess.devices.datasinks.file_writer.FileWriterStatus',
        description = 'Status of the file-writer',
        brokers = configdata('config.KAFKA_BROKERS'),
        statustopic = 'AMOR_filewriter',
        unit = '',
    ),
    FileWriterControl = device('nicos_sinq.devices.datasinks.SinqFileWriterControlSink',
        description = 'Control for the file-writer',
        brokers = configdata('config.KAFKA_BROKERS'),
        pool_topic = 'AMOR_filewriterPool',
        status = 'FileWriterStatus',
        nexus = 'NexusStructure',
        file_output_dir = configdata('config.DATA_PATH'),
        filenametemplate = ['amor%(year)sn%(pointcounter)06d.hdf'],
        visibility = ('namespace', 'devlist'),
    ),
    NexusStructure = device('nicos_sinq.amor.devices.datasinks.AmorStructureTemplate',
        description = 'Provides the NeXus structure',
        templatesmodule = 'nicos_sinq.amor.nexus.nexus_templates',
        templatename = 'amor_streaming',
    ),
    proton_current = device('nicos_sinq.devices.epics.proton_counter.SINQProtonCurrent',
        description = 'Proton current',
        readpv = 'SQ:AMOR:sumi:BEAMCPY',
        unit = 'uA',
        fmtstr = '%6.1f',
    ),
    ltz_sim = device('nicos.devices.generic.manual.ManualMove',
        description = 'Deflector vertical translation',
        unit = 'mm',
        abslimits = (-40, 200),
        default = 0
    ),
    lom_sim = device('nicos.devices.generic.manual.ManualMove',
        description = 'Deflector rotation',
        unit = 'deg',
        abslimits = (-10, 10),
        default = 0,
    ),
    lom = device('nicos.core.device.DeviceAlias',
        description = 'Alias for lom',
        alias = 'lom_sim',
        devclass = 'nicos.core.device.Moveable'
    ),
    ltz = device('nicos.core.device.DeviceAlias',
        description = 'Alias for ltz',
        alias = 'ltz_sim',
        devclass = 'nicos.core.device.Moveable'
        ),
    syncdaqsink = device('nicos_sinq.amor.devices.datasinks.SyncDaqSink',
        description = 'Sink for synchronizing the DAQ PC and the ring modules at the start of each measurement'
    ),
)
