# A detailed description of the setup file structure and it's elements is
# available here: https://forge.frm2.tum.de/nicos/doc/nicos-stable/setups/
#
# Please remove these lines after copying this file.

description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    # Adapt this name to your instrument's name (also below).
    instrument = 'cvtutomo',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink'],
    notifiers = [],  # ['email'],
)

modules = [
    'nicos.commands.standard',
    'nicos_mlz.antares.commands',
]

includes = [
    'notifiers',
]

devices = dict(
    cvtutomo = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'CVTU-Tomo',
        responsible = 'Jana Matoušková <jana.matouskova@fjfi.cvut.cz>',
        website = 'https://fjfi.cvut.cz/en/',
        operators = ['České vysoké učení technické v Praze'],
        facility = 'Centrum výzkumu Řež s.r.o (CVŘ)',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),

    # Configure dataroot here (usually /data).
    Exp = device('nicos.devices.experiment.ImagingExperiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = True,
        sample = 'Sample',
        managerights = {
            'owner': 'nicd',
            'group': 'users',
        },
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = '/data',
        warnlimits = (5., None),
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = '/control/log',
        warnlimits = (.5, None),
        minfree = 0.5,
        visibility = (),
    ),
)
