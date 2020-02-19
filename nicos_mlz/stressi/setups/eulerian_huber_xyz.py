description = 'STRESS-SPEC setup with Huber Eulerian cradle plus small xyz table'

group = 'basic'

includes = [
    'eulerian_huber',
]

sysconfig = dict(
    datasinks = ['caresssink'],
)

tango_base = 'tango://motorbox05.stressi.frm2.tum.de:10000/box/'

devices = dict(
    xe_m = device('nicos.devices.tango.Motor',
        tangodevice = tango_base + 'channel1/motor',
        speed = 1,
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    xe = device('nicos.devices.generic.Axis',
        description = 'X Eulerian XYZ',
        fmtstr = '%.2f',
        motor = 'xe_m',
        precision = 0.01,
    ),
    ye_m = device('nicos.devices.tango.Motor',
        tangodevice = tango_base + 'channel2/motor',
        speed = 1,
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    ye = device('nicos.devices.generic.Axis',
        description = 'Y Eulerian XYZ',
        fmtstr = '%.2f',
        motor = 'ye_m',
        precision = 0.01,
    ),
    ze_m = device('nicos.devices.tango.Motor',
        tangodevice = tango_base + 'channel3/motor',
        speed = 1,
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    ze = device('nicos.devices.generic.Axis',
        description = 'Z Eulerian XYZ',
        fmtstr = '%.2f',
        motor = 'ze_m',
        precision = 0.01,
    ),
)
