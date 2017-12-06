# -*- coding: utf-8 -*-

description = 'Coil setup'
group = 'lowlevel'

tango_base = 'tango://phys.dns.frm2:10000/dns/'

##
# magnetic field definitions on 13-03-2015/20-03-2015
off     = (0, 0, 0, 0, 0, (0, 0), 'off', 0)
zero    = (0, .15, -.50, -2.15, -2.15, (0, 0), 'off', 0)
# fields with spin flipper
zero_sf = (0, .15, -.50, -2.15, -2.15, (-0.95,-0.35), 'on', 0)
x7_sf   = (-0.5, -1.5, -1.20, -2.15, -2.15, (-0.925,-0.45), 'on', 0)
x20_sf  = (-0.5, -1.5, -1.20, -2.15, -2.15, (-0.9,-0.58), 'on', 0)
# x7_old: (0.94,0.40)
mx7_sf  = (0, 2.30, -0.35, -2.15, -2.15, (-0.9, -0.5), 'on', 0)
# y7 and my7 swapped, 22-july-2016
my7_sf   = (-0.3, 2.0, -2.95, -2.15, -2.15, (-0.85,-0.53), 'on', 0)
# y7_old: (0.945,0.31)/(0.98,0.32)
# was (1.0,0.15) before 20.05.15; changed to (1.0,0.32) on 20.05.15
y7_sf  = (0, -1.40, 1.65, -2.15, -2.15, (-0.95, -0.4), 'on', 0)
y20_sf = (0, -1.40, 1.65, -2.15, -2.15, (-0.95, -0.5), 'on', 0)
#
z7_sf   = (0, .15, -.50, 0.0, 0.0, (-0.95,-0.4), 'on', 0)
z20_sf  = (0, .15, -.50, 0.0, 0.0, (-0.9,-0.53), 'on', 0)
# z7_old: (0.94,0.35)
mz7_sf  = (0, .15, -.50, -4.3, -4.3, (-0.9,-0.5), 'on', 0)
z7_high_sf   = (0, .15, -.50, 5.0, 5.0, (-0.925,-0.35), 'on', 0)
z7_default_sf   = (0, 0, 0, 0, 0, (-0.95,-0.35), 'on', 0)
#old ZB=ZT=4A
# fields without spin flipper
zero_nsf = zero_sf[:6] + ('off', 0)
x7_nsf   = x7_sf[:6]  + ('off', 0)
x20_nsf  = x20_sf[:6] + ('off', 0)
mx7_nsf  = mx7_sf[:6] + ('off', 0)
y7_nsf   = y7_sf[:6]  + ('off', 0)
y20_nsf  = y20_sf[:6] + ('off', 0)
my7_nsf  = my7_sf[:6] + ('off', 0)
z7_nsf   = z7_sf[:6]  + ('off', 0)
mz7_nsf  = mz7_sf[:6] + ('off', 0)
z7_high_nsf = z7_high_sf[:6] + ('off', 0)
z7_default_nsf = z7_default_sf[:6] + ('off', 0)
z20_nsf  = z20_sf[:6] + ('off', 0)

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
    polch_Fi = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Polarity changer for Flipper Field',
        tangodevice = tango_base + 'fzjdp_digital/polum1',
        mapping = polchange_mapping,
        lowlevel = True
    ),
    # Devices for toellner must be changed with new names from database
    Fi = device('nicos_mlz.dns.devices.toellner.Toellner',
        description = 'Flipper Field',
        tangodevice = tango_base + 'toellner/fi',
        abslimits = (-3.25, 3.25),
        polchange = 'polch_Fi',
    ),
    polch_Co = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Polarity changer for Flipper Compensation',
        tangodevice = tango_base + 'fzjdp_digital/polum2',
        mapping = polchange_mapping,
        lowlevel = True
    ),
    Co = device('nicos_mlz.dns.devices.toellner.Toellner',
        description = 'Flipper Compensation Field',
        tangodevice = tango_base + 'toellner/co',
        abslimits = (-3.25, 3.25),
        polchange = 'polch_Co',
    ),
    A = device('nicos_mlz.dns.devices.toellner.Toellner',
        description = 'Coil A',
        tangodevice = tango_base + 'toellner/a',
        abslimits = (-3.25, 3.25),
        polchange = 'polch_A',
    ),
    polch_A = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Polarity changer for coil A',
        tangodevice = tango_base + 'fzjdp_digital/polum3',
        mapping = polchange_mapping,
        lowlevel = True,
    ),
    B = device('nicos_mlz.dns.devices.toellner.Toellner',
        description = 'Coil B',
        tangodevice = tango_base + 'toellner/b',
        abslimits = (-3.25, 3.25),
        polchange = 'polch_B',
    ),
    polch_B = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Polarity changer for coil B',
        tangodevice = tango_base + 'fzjdp_digital/polum4',
        mapping = polchange_mapping,
        lowlevel = True,
    ),
    ZB = device('nicos_mlz.dns.devices.toellner.Toellner',
        description = 'Coil-Z Bottom',
        tangodevice = tango_base + 'toellner/zb',
        abslimits = (-5, 5),
        polchange = 'polch_ZB',
    ),
    polch_ZB = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Polarity changer for coil Z Bottom',
        tangodevice = tango_base + 'fzjdp_digital/polum5',
        mapping = polchange_mapping,
        lowlevel = True,
    ),
    ZT = device('nicos_mlz.dns.devices.toellner.Toellner',
        description = 'Coil-Z Top',
        tangodevice = tango_base + 'toellner/zt',
        abslimits = (-5, 5),
        polchange = 'polch_ZT',
    ),
    polch_ZT = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Polarity changer for coil Z Top',
        tangodevice = tango_base + 'fzjdp_digital/polum6',
        mapping = polchange_mapping,
        lowlevel = True,
    ),
    C = device('nicos_mlz.dns.devices.toellner.Toellner',
        description = 'Coil C',
        tangodevice = tango_base + 'toellner/c',
        abslimits = (-3.25, 3.25),
        polchange = 'polch_C',
    ),
    polch_C = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Polarity changer for coil C',
        tangodevice = tango_base + 'fzjdp_digital/polum7',
        mapping = polchange_mapping,
        lowlevel = True,
    ),
    field_freq = device('nicos.devices.tango.AnalogOutput',
        description = 'Frequency of switched field',
        tangodevice = tango_base + 'agilent/freq',
    ),
    field_dutycycle = device('nicos.devices.tango.AnalogOutput',
        description = 'Duty cycle of switched field',
        tangodevice = tango_base + 'agilent/symm',
        fmtstr = '%d',
    ),
    field = device('nicos.devices.generic.MultiSwitcher',
        description = 'Guide field switcher',
        moveables = [
            'A', 'B', 'C', 'ZB', 'ZT', 'flip_currents', 'flipper', 'field_freq'
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
            'z7_default_sf': z7_default_sf,
            'z7_default_nsf': z7_default_nsf,
            'x20_nsf': x20_nsf,
            'x20_sf': x20_sf,
            'y20_nsf': y20_nsf,
            'y20_sf': y20_sf,
            'z20_nsf': z20_nsf,
            'z20_sf': z20_sf,
        },
        precision = [.1, .1, .1, .1, .1, 0, 0, 10000],
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
