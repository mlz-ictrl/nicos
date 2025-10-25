description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = configdata('config_data.cache_host'),
    instrument = 'REFSANS',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'configsink'],
#   notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.refsans.commands']

devices = dict(
    REFSANS = device('nicos.devices.instrument.Instrument',
        description = 'Container storing Instrument properties',
        instrument = 'REFSANS',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-31',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        operators = ['NICOS developer team'],
        website = 'http://www.mlz-garching.de/refsans',
        facility = 'NICOS demo instruments',
    ),
    Sample = device('nicos_virt_mlz.refsans.devices.sample.Sample',
        description = 'Container storing Sample properties',
        datapath = '/usr/local/share/mcstas/data/refsans',
        width = 50,
        length = 80,
        samples = {
            1: {'name': 'Standard', 'sample_file': 'Si_Ti_Al_Mirror.dat'},
        }
    ),
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'Container storing Experiment properties',
        dataroot = configdata('config_data.dataroot'),
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    configsink = device('nicos_mlz.refsans.datasinks.ConfigObjDatafileSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        minfree = 5,
        path = configdata('config_data.dataroot'),
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = configdata('config_data.logging_path'),
        visibility = (),
        warnlimits = (0.5, None),
    ),
)
