description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'TSpec',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink', 'sraw'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = [
    'notifiers',
]

devices = dict(
    TSpec = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'T-SPEC',
        responsible = 'A. Sizov <sizov_aa@nrcki.pnpi.ru>',
        facility = 'PNPI',
        website = 'http://www.pnpi.spb.ru/en/facilities/reactor-pik',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'My sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        # Configure dataroot here (usually /data).
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    sraw = device('nicos.devices.datasinks.SingleTextImageSink'),
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'Timer',
    ),
    # PEX48 = device('nicos.devices.entangle.CounterChannel',
    #    tangodevice = 'tango://localhost:10000/nspex48/nspex48/1',
    #    type = 'monitor',
    # ),
    NsRV16115 = device('nicos.devices.entangle.TOFChannel',
        tangodevice = 'tango://localhost:10000/nsrv16115/nsrv16115/1',
        lowlevel = True,
    ),
    NsRV16115WL = device('nicos.devices.entangle.TOFChannel',
        tangodevice = 'tango://localhost:10000/nsrv16115wl/nsrv16115wl/1',
        lowlevel = True,
    ),
    detector = device('nicos.devices.generic.Detector',                # сам детектор
        description = 'USB detector RV161_15 and PCI monitor PEX_D48',
        timers = ['timer'],
        # monitors = ['PEX48'],
        images = ['NsRV16115WL'] #,'NsRV16115'],
    ),
    detector2 = device('nicos.devices.generic.Detector',               # сам детектор
        description = '2',
        timers = ['timer'],
        # monitors = ['PEX48'],
        images = ['NsRV16115'],
    ),
    # chopper_position = device('nicos.devices.entangle.Motor',
    #    description = 'Движение',
    #    tangodevice = 'tango://localhost:10000/nsra153_28_choper/nsra153_28_choper_instance/1',
    # ),
    # detector_position = device('nicos.devices.entangle.Motor',
    #    description = 'Движение',
    #    tangodevice = 'tango://localhost:10000/nsra153_28_detector/nsra153_28_detector_instance/1',
    # ),
)
