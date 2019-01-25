# -*- coding: utf-8 -*-

description = 'Polarizer motor setup'
group = 'lowlevel'
display_order = 25

excludes = ['virtual_polarizer']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    polarizer = device('nicos_mlz.kws1.devices.polarizer.Polarizer',
        description = 'high-level polarizer switcher',
        switcher = 'pol_switch',
        switchervalues = ('out', 'in'),
        flipper = 'flipper',
    ),
    pol_switch = device('nicos.devices.generic.MultiSwitcher',
        description = 'select polarizer presets',
        blockingmove = False,
        moveables = ['pol_y', 'pol_tilt'],
        mapping = {
            'out': [5, 0],
            'in':  [25.5, 0],
        },
        fallback = 'unknown',
        precision = [0.01, 0.01],
    ),
    pol_y = device('nicos.devices.tango.Motor',
        description = 'polarizer y-table',
        tangodevice = s7_motor + 'pol_y',
        unit = 'mm',
        precision = 0.01,
    ),
    pol_tilt = device('nicos.devices.tango.Motor',
        description = 'polarizer tilt',
        tangodevice = s7_motor + 'pol_tilt',
        unit = 'deg',
        precision = 0.01,
    ),
    flip_set = device('nicos.devices.tango.DigitalOutput',
        tangodevice = tango_base + 's7_digital/flipper',
        lowlevel = True,
    ),
    flip_ps = device('nicos.devices.tango.PowerSupply',
        tangodevice = tango_base + 'flipperps/volt',
        lowlevel = True,
        abslimits = (0, 20),
        timeout = 3,
    ),
    flipper = device('nicos_mlz.kws1.devices.flipper.Flipper',
        description = 'spin flipper after polarizer',
        output = 'flip_set',
        supply = 'flip_ps',
    ),
)

extended = dict(
    representative = 'polarizer',
)
