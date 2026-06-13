description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'NSE',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = [
    'notifiers',
    'coiltemp',
    'reactor',
    'guidehall',
    'nl2a',
    'memograph',
]

devices = dict(
    NSE = device('nicos_mlz.j_nse.devices.instrument.JnseInstrument',
        description = 'instrument object',
        instrument = 'JNSE',
        responsible = 'O. Holderer <o.holderer@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
        website = 'http://www.mlz-garching.de/j-nse',
        table_filename = '/control/nicos_mlz/j_nse/NIST_table.csv',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        # cannot use /data until main instrument control is switched to NICOS
        dataroot = '/home/jcns/nicos-data',
        sendmail = True,
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
