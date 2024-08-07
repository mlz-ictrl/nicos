description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = configdata('config_data.host'),
    instrument = 'NRS',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = [
    'nicos.commands.standard',
    'nicos_mlz.antares.commands',
]

devices = dict(
    Sample = device('nicos.devices.experiment.Sample',
        description = 'Default Sample',
    ),
    Exp = device('nicos.devices.experiment.ImagingExperiment',
        description = 'North radiography station experiment',
        dataroot = configdata('config_data.dataroot'),
        sample = 'Sample',
        mailsender = 'aaron.craft@inl.gov',
        propprefix = '',
        strictservice = True,
        templates = 'templates',
        zipdata = False,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o775,
            disableFileMode = 0o664,
        ),
    ),
    NRS = device('nicos.devices.instrument.Instrument',
        description = 'North radiography station',
        instrument = 'NRS',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        operators = ['NICOS developer team'],
        website = 'http://mfc.inl.gov',
        facility = 'NICOS demo instruments',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    DataSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space on the DataStorage',
        path = configdata('config_data.dataroot'),
        minfree = 5,
    ),
)
