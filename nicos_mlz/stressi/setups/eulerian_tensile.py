description = 'STRESS-SPEC setup with Tensile rig Eulerian cradle'

group = 'basic'

includes = [
    'standard',
    'sampletable',
]

sysconfig = dict(
    datasinks = ['caresssink'],
)

tango_base = 'tango://motorbox06.stressi.frm2.tum.de:10000/box/'

devices = dict(
    chis_m = device('nicos.devices.tango.Motor',
        fmtstr = '%.2f',
        tangodevice = tango_base + 'channel5/motor',
        lowlevel = True,
    ),
    chis_c = device('nicos.devices.tango.Sensor',
        tangodevice = tango_base + 'channel5/coder',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    chis = device('nicos.devices.generic.Axis',
        description = 'Tensile CHIS',
        motor = 'chis_m',
        coder = 'chis_c',
        precision = 0.01,
    ),
    phis_m = device('nicos.devices.tango.Motor',
        tangodevice = tango_base + 'channel6/motor',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    phis = device('nicos.devices.generic.Axis',
        description = 'Tensile PHIS',
        motor = 'phis_m',
        precision = 0.01,
    ),
)
