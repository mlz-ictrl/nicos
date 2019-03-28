# -*- coding: utf-8 -*-

description = 'DNS polarizer'
group = 'lowlevel'

tango_base = 'tango://phys.dns.frm2:10000/dns/'

# mapping at 4.74A 'pol_trans_x', 'pol_trans_y', 'pol_rot'
POLARIZER_POSITIONS = {
    'in':  [3 , 0, -2.0],
    'out': [3, 100, -2.0],
}

## mapping at 5.7A 'pol_trans_x', 'pol_trans_y', 'pol_rot'
#POLARIZER_POSITIONS = {
#    'in':  [3 , 0, -2.2],
#    'out': [3, 100, -2.2],
#}


devices = dict(
    pol_inbeam = device('nicos.devices.generic.MultiSwitcher',
        description = 'Automatic in/out switch for the polarizer',
        mapping = POLARIZER_POSITIONS,
        fallback = 'unknown',
        moveables = ['pol_trans_x', 'pol_trans_y', 'pol_rot'],
        precision = [0.1, 0.1, 0.1],
    ),
    pol_trans_x = device('nicos.devices.tango.Motor',
        description = 'Polarizer translation left-right',
        tangodevice = tango_base + 's7_motor/pol_trans_x',
    ),
    pol_trans_y = device('nicos.devices.tango.Motor',
        description = 'Polarizer translation up-down',
        tangodevice = tango_base + 's7_motor/pol_trans_y',
    ),
    pol_rot = device('nicos.devices.tango.Motor',
        description = 'Polarizer rotation',
        tangodevice = tango_base + 's7_motor/pol_rot',
    ),
    pol_x_left = device('nicos_mlz.jcns.devices.motor.Motor',
        description = 'Aperture polarizer x left',
        tangodevice = tango_base + 's7_motor/pol_x_left',
        lowlevel = False,
        precision = 0.1,
    ),
    pol_x_right = device('nicos_mlz.jcns.devices.motor.Motor',
        description = 'Aperture polarizer x right',
        tangodevice = tango_base + 's7_motor/pol_x_right',
        lowlevel = False,
        precision = 0.1,
    ),
    pol_y_upper = device('nicos_mlz.jcns.devices.motor.Motor',
        description = 'Aperture polarizer y upper',
        tangodevice = tango_base + 's7_motor/pol_y_upper',
        lowlevel = False,
        precision = 0.1,
    ),
    pol_y_lower = device('nicos_mlz.jcns.devices.motor.Motor',
        description = 'Aperture polarizer y lower',
        tangodevice = tango_base + 's7_motor/pol_y_lower',
        lowlevel = False,
        precision = 0.1,
    ),
    pol_slit = device('nicos.devices.generic.Slit',
        description = 'Polarizer slit',
        left = 'pol_x_left',
        right = 'pol_x_right',
        bottom = 'pol_y_lower',
        top = 'pol_y_upper',
        coordinates = 'equal',
        opmode = 'offcentered',
    ),
)

extended = dict(
    representative = 'pol_inbeam',
)
