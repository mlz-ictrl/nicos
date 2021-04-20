# -*- coding: utf-8 -*-

description = 'Coil setup'
group = 'lowlevel'

tango_base = 'tango://phys.dns.frm2:10000/dns/'

##
# magnetic field definitions on 06/04/2021
off     = (0, 0, 0, 0, 0, (0, 0), 'off')
zero    = (0, .095, -.45, -2.27, -2.27, (0, 0), 'off')
#  with spin flipper
zero_sf = (0, .095, -.45, -2.27, -2.27, (-0.95,-0.35), 'on')

# x
x7_sf   = (0, -0.8, -0.5, -2.325, -2.325, (-0.8,-0.46), 'on')
x20_sf  = (0, -0.8, -0.5, -2.325, -2.325, (-0.9,-0.58), 'on')
mx7_sf  = (0, 0.705, -0.4, -2.22, -2.22, (-0.8, -0.46), 'on')

# y:
y7_sf  = (0, -0.9, 0.9, -2.47, -2.47, (-0.8, -0.43), 'on')
y20_sf = (0, -0.9, 0.9, -2.47, -2.47, (-0.95, -0.5), 'on')
my7_sf   = (0, 0.805, -1.35, -2.13, -2.13, (-0.8,-0.43), 'on')

# z
z7_sf   = (0, .095, -.45, 0.0, 0.0, (-0.80,-0.45), 'on')
z20_sf  = (0, .095, -.45, 0.0, 0.0, (-0.9,-0.53), 'on')
mz7_sf  = (0, .095, -.45, -1, -1, (-0.9,-0.5), 'on')
z7_high_sf   = (0, .095, -.45, 5.0, 5.0, (-0.925,-0.35), 'on')

#z7_default_sf   = (0, 0, 0, 0, 0, (-0.95,-0.35), 'on')
#old ZB=ZT=4A
# fields without spin flipper
zero_nsf = zero_sf[:6] + ('off',)
x7_nsf   = x7_sf[:6]  + ('off',)
x20_nsf  = x20_sf[:6] + ('off',)
mx7_nsf  = mx7_sf[:6] + ('off',)
y7_nsf   = y7_sf[:6]  + ('off',)
y20_nsf  = y20_sf[:6] + ('off',)
my7_nsf  = my7_sf[:6] + ('off',)
z7_nsf   = z7_sf[:6]  + ('off',)
mz7_nsf  = mz7_sf[:6] + ('off',)
z7_high_nsf = z7_high_sf[:6] + ('off',)
#z7_default_nsf = z7_default_sf[:6] + ('off',)
z20_nsf  = z20_sf[:6] + ('off',)

polchange_mapping = {'+': 0, '-': 1}


devices = dict(
    flipper = device('nicos.devices.polarized.flipper.MezeiFlipper',
        description = 'Neutron spin flipper',
        flip = 'Fi',
        corr = 'Co',
    ),
    flip_currents = device('nicos.devices.generic.ParamDevice',
        description = 'Helper device for setting the'
        'currents on the flipper device as a '
        'moveable',
        device = 'flipper',
        parameter = 'currents',
        unit = 'A',
        lowlevel = True,
    ),

    Fi = device('nicos.devices.entangle.PowerSupply',
        description = 'Flipper Field',
        tangodevice = tango_base + 'toellner/fi',
        abslimits = (-3.25, 3.25),
    ),
    Co = device('nicos.devices.entangle.PowerSupply',
        description = 'Flipper Compensation Field',
        tangodevice = tango_base + 'toellner/co',
        abslimits = (-3.25, 3.25),
    ),

    A = device('nicos.devices.entangle.PowerSupply',
        description = 'Coil A',
        tangodevice = tango_base + 'toellner/a',
        abslimits = (-3.25, 3.25),
    ),
    B = device('nicos.devices.entangle.PowerSupply',
        description = 'Coil B',
        tangodevice = tango_base + 'toellner/b',
        abslimits = (-3.25, 3.25),
    ),
    ZB = device('nicos.devices.entangle.PowerSupply',
        description = 'Coil-Z Bottom',
        tangodevice = tango_base + 'toellner/zb',
        abslimits = (-5, 5),
    ),
    ZT = device('nicos.devices.entangle.PowerSupply',
        description = 'Coil-Z Top',
        tangodevice = tango_base + 'toellner/zt',
        abslimits = (-5, 5),
    ),
    C = device('nicos.devices.entangle.PowerSupply',
        description = 'Coil C',
        tangodevice = tango_base + 'toellner/c',
        abslimits = (-3.25, 3.25),
    ),

#    field_freq = device('nicos.devices.entangle.AnalogOutput',
#        description = 'Frequency of switched field',
#        tangodevice = tango_base + 'agilent/freq',
#    ),
#    field_dutycycle = device('nicos.devices.entangle.AnalogOutput',
#        description = 'Duty cycle of switched field',
#        tangodevice = tango_base + 'agilent/symm',
#        fmtstr = '%d',
#    ),

    field = device('nicos_mlz.dns.devices.coils.MultiSwitcher',
        description = 'Guide field switcher',
        moveables = [
#            'A', 'B', 'C', 'ZB', 'ZT', 'flip_currents', 'flipper', 'field_freq'
            'A', 'B', 'C', 'ZB', 'ZT', 'flip_currents', 'flipper',
        ],
        mapping = {
            'off': off,
            'zero field': zero,
            'zero_sf': zero_sf,
            'zero_nsf': zero_nsf,
            'x7_sf': x7_sf,
            '-x7_sf': mx7_sf,
            'y7_sf': y7_sf,
            '-y7_sf': my7_sf,
            'z7_sf': z7_sf,
            '-z7_sf': mz7_sf,
            'x7_nsf': x7_nsf,
            '-x7_nsf': mx7_nsf,
            'y7_nsf': y7_nsf,
            '-y7_nsf': my7_nsf,
            'z7_nsf': z7_nsf,
            '-z7_nsf': mz7_nsf,
            'z7_high_sf': z7_high_sf,
            'z7_high_nsf': z7_high_nsf,
            #'z7_default_sf': z7_default_sf,
            #'z7_default_nsf': z7_default_nsf,
            'x20_nsf': x20_nsf,
            'x20_sf': x20_sf,
            'y20_nsf': y20_nsf,
            'y20_sf': y20_sf,
            'z20_nsf': z20_nsf,
            'z20_sf': z20_sf,
        },
        precision = [.1, .1, .1, .1, .1, 0, 0,],
        blockingmove = False,
    ),
    flipper_inbeam = device('nicos.devices.generic.ManualSwitch',
        description = 'Is the flipper in the beam?',
        states = ['in', 'out'],
    ),
    xyzcoil_inbeam = device('nicos.devices.generic.ManualSwitch',
        description = 'Is the xyz-coil in the beam?',
        states = ['in', 'out'],
    ),
)

extended = dict(
    representative = 'field',
)
