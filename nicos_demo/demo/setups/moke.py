description = 'virtual MOKE setup'
group = 'basic'

sysconfig = dict(
    instrument = 'moke',
    datasinks = ['filesink',],
)

from nicos.utils.functioncurves import Curves
from nicos_jcns.moke01.utils import generate_intvb

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'sample object',
    ),
    moke = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        instrument = 'MOKE',
        website = 'https://www.nicos-controls.org',
        operators = ['NICOS developer team'],
        facility = 'NICOS demo instruments',
    ),
    PS_current = device('nicos_jcns.moke01.devices.virtual.VirtualPowerSupply',
        unit = 'A',
        abslimits = (-1000, 1000),
        ramp = 1e4,
        maxramp = 1e6,
        fmtstr = '%.1f',
    ),
    Mag_sensor = device('nicos_jcns.moke01.devices.virtual.VirtualMokeSensor',
        mappeddevice = 'PS_current',
        unit = 'mT',
        valuemap = Curves([[(-1000, -1000), (-250, -750), (300, 750), (1000, 1000)],
                           [(1000, 1000), (250, 750), (-300, -750), (-1000, -1000)]]),
        error = 0.01,
        pollinterval = 0.5,
    ),
    Intensity = device('nicos_jcns.moke01.devices.virtual.VirtualMokeSensor',
        mappeddevice = 'Mag_sensor',
        unit = 'mV',
        valuemap = generate_intvb(-1000, 1000),
        error = 0.002,
        pollinterval = 0.5,
    ),
    MagB = device('nicos_jcns.moke01.devices.virtual.VirtualMokeMagnet',
        unit = 'mT',
        intensity = 'Intensity',
        magsensor = 'Mag_sensor',
        currentsource = 'PS_current',
        calibration = {
            'stepwise': {
                '10000.0':
                    Curves([[(-1000, -1000), (-250, -750), (300, 750), (1000, 1000)],
                            [(1000, 1000), (250, 750), (-300, -750), (-1000, -1000)]])
            },
            'continuous': {
            },
        },
        ramp = 1e4,
        maxramp = 1e6,
        pollinterval = 0.5,
        fmtstr = '%.3f',
    ),
)

startupcode = '''
printinfo("============================================================")
printinfo("Welcome to the NICOS MOKE demo setup.")
printinfo("============================================================")
'''
