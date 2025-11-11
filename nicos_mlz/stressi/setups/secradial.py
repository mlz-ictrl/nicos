description = 'Radialcollimator devices diffracted beam'

group = 'optional'

tango_base = 'tango://motorbox03.stressi.frm2.tum.de:10000/box/'

excludes = ['secondaryslit']

devices = dict(
    rcd_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel7/motor',
        fmtstr = '%.3f',
        visibility = (),
    ),
    rcd_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'channel7/coder',
        fmtstr = '%.3f',
        visibility = (),
    ),
    rcd = device('nicos.devices.generic.Axis',
        description = 'Radial collimator horizontal tilt (RadColli=ZE)',
        fmtstr = '%.3f',
        motor = 'rcdet_m',
        coder = 'rcdet_c',
        precision = 0.01,
    ),
    ssw = device('nicos_mlz.stressi.devices.SingleAxisGap',
        description = 'Secondary radial collimator width (Gauge volume depth)',
        moveable = device('nicos_mlz.stressi.devices.PreciseManualSwitch',
            fmtstr = '%.1f',
            unit = 'mm',
            states = (0.5, 1, 2, 5, 10, 20),
            requires = {'level': 'admin'},
        ),
        autodevice_visibility = {'metadata', },
    ),
    yss = device('nicos.devices.generic.ManualMove',
        description = 'Distance sample detector collimator',
        default = 1100.,
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (800, 1300),
    ),
)
