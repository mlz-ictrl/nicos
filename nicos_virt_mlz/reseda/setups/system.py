description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'vreseda',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink', 'LiveImgSink'],
    notifiers = [],
)

modules = ['nicos.commands.standard', 'nicos_mlz.reseda.tuning_commands',  'nicos_mlz.reseda.commands']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'The sample',
    ),
    vreseda = device('nicos.devices.instrument.Instrument',
        description = 'Resonance spin echo spectrometer',
        instrument = 'VRESEDA',
        responsible = 'Christian Franz <christian.franz@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-37',
        website = 'http://www.mlz-garching.de/reseda',
        operators = ['Technische Universität München (TUM)'],
    ),
    Exp = device('nicos_mlz.reseda.devices.experiment.Experiment',
        description = 'Experiment object',
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'p0',
        sample = 'Sample',
        mailsender = 'reseda@frm2.tum.de',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
    ),
    DataSpace = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = 'data',
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = 'log',
        warnlimits = (.5, None),
        minfree = 0.5,
        lowlevel = True,
    ),
    LiveImgSink = device('nicos.devices.datasinks.PNGLiveFileSink',
        description = 'Saves live image as .png every now and then',
        filename = 'data/live.png',
        interval = 1,
    ),
)

startupcode = '''
from nicos.core import SIMULATION
if not Exp.proposal and Exp._mode != SIMULATION:
    try:
        SetMode('master')
    except Exception:
        pass
    else:
        NewExperiment(0, 'NICOS demo experiment',
                      localcontact='Nico Suser <nico.suser@frm2.tum.de>')
        AddUser('H. Maier-Leibnitz <heinz.maier-leibnitz@frm2.tum.de')
        NewSample('Gd3CdB7')
'''
