# -*- coding: utf-8 -*-

description = "Coil setup"
group = "optional"

tango_base = 'tango://phys.dns.frm2:10000/dns/'

##
# magnetic field definitions on 13-03-2015/20-03-2015
off     = (0, 0, 0, 0, 0, (0, 0), "off")
zero    = (0, .15, -.50, -2.15, -2.15, (0.0, 0.0), "off")
# fields with spin flipper
x7_sf   = (-0.5, -1.5, -1.20, -2.15, -2.15, (1.0,0.25), "on")
# x7_old: (0.94,0.40)
mx7_sf  = (0, 2.30, -0.35, -2.15, -2.15, (1.05, 0.38), "on")
y7_sf   = (-0.3, 2.0, -2.95, -2.15, -2.15, (1.0,0.32), "on")
# y7_old: (0.945,0.31)/(0.98,0.32)
# was (1.0,0.15) before 20.05.15; changed to (1.0,0.32) on 20.05.15
my7_sf  = (0, -1.40, 1.65, -2.15, -2.15, (0.98, 0.38), "on")
z7_sf   = (0, .15, -.50, 0.0, 0.0, (1.0,0.20), "on")
# z7_old: (0.94,0.35)
mz7_sf  = (0, .15, -.50, -4.3, -4.3, (1.00, 0.20), "on")
z7_high_sf   = (0, .15, -.50, 5.0, 5.0, (1.0,0.15), "on")
#old ZB=ZT=4A
# fields without spin flipper
x7_nsf  = x7_sf[:6] + ("off", )
mx7_nsf = mx7_sf[:6] + ("off", )
y7_nsf  = y7_sf[:6] + ("off", )
my7_nsf = my7_sf[:6] + ("off", )
z7_nsf  = z7_sf[:6] + ("off", )
mz7_nsf = mz7_sf[:6] + ("off", )
z7_high_nsf = z7_high_sf[:6] + ('off',)

polchange_mapping = {"+": 0, "-": 1}


devices = dict(
    flipper       = device('devices.polarized.flipper.MezeiFlipper',
                           description = 'Neutron spin flipper',
                           flip = "Fi",
                           corr = "Co",
                          ),
    flip_currents = device('devices.generic.ParamDevice',
                           description = 'Helper device for setting the'
                                         'currents on the flipper device as a '
                                         'moveable',
                           device = 'flipper',
                           parameter = 'currents',
                           unit = 'A',
                           lowlevel = True,
                          ),
    polch_Fi = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for Flipper Field',
                      tangodevice = tango_base + 'fzjdp_digital/polum1',
                      mapping = polchange_mapping,
                      lowlevel = True
                     ),
# Devices for toellner must be changed with new names from database
    Fi       = device('dns.toellner.Toellner',
                      description = 'Flipper Field',
                      tangodevice = tango_base + 'toellner/fi',
                      abslimits = (-3.2, 3.2),
                      polchange = 'polch_Fi',
                     ),
    polch_Co = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for Flipper Compensation',
                      tangodevice = tango_base + 'fzjdp_digital/polum2',
                      mapping = polchange_mapping,
                      lowlevel = True
                     ),
    Co       = device('dns.toellner.Toellner',
                      description = 'Flipper Compensation Field',
                      tangodevice = tango_base + 'toellner/co',
                      abslimits = (-3.2, 3.2),
                      polchange = 'polch_Co',
                     ),
    A        = device('dns.toellner.Toellner',
                      description = 'Coil A',
                      tangodevice = tango_base + 'toellner/a',
                      abslimits = (-3.2, 3.2),
                      polchange = 'polch_A',
                     ),
    polch_A  = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for coil A',
                      tangodevice = tango_base + 'fzjdp_digital/polum3',
                      mapping = polchange_mapping,
                      lowlevel = True,
                     ),
    B        = device('dns.toellner.Toellner',
                      description = 'Coil B',
                      tangodevice = tango_base + 'toellner/b',
                      abslimits = (-3.2, 3.2),
                      polchange = 'polch_B',
                     ),
    polch_B  = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for coil B',
                      tangodevice = tango_base + 'fzjdp_digital/polum4',
                      mapping = polchange_mapping,
                      lowlevel = True,
                     ),
    ZB       = device('dns.toellner.Toellner',
                      description = 'Coil-Z Bottom',
                      tangodevice = tango_base + 'toellner/zb',
                      abslimits = (-5, 5),
                      polchange = 'polch_ZB',
                     ),
    polch_ZB = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for coil Z Bottom',
                      tangodevice = tango_base + 'fzjdp_digital/polum5',
                      mapping = polchange_mapping,
                      lowlevel = True,
                     ),
    ZT       = device('dns.toellner.Toellner',
                      description = 'Coil-Z Top',
                      tangodevice = tango_base + 'toellner/zt',
                      abslimits = (-5, 5),
                      polchange = 'polch_ZT',
                     ),
    polch_ZT = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for coil Z Top',
                      tangodevice = tango_base + 'fzjdp_digital/polum6',
                      mapping = polchange_mapping,
                      lowlevel = True,
                     ),
    C        = device('dns.toellner.Toellner',
                      description = 'Coil C',
                      tangodevice = tango_base + 'toellner/c',
                      abslimits = (-3.2, 3.2),
                      polchange = 'polch_C',
                     ),
    polch_C  = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for coil C',
                      tangodevice = tango_base + 'fzjdp_digital/polum7',
                      mapping = polchange_mapping,
                      lowlevel = True,
                     ),
    field    = device('devices.generic.MultiSwitcher',
                      description = 'Guide field switcher',
                      moveables = ["A", "B", "C", "ZB", "ZT",
                                   "flip_currents", "flipper"],
                      mapping = {
                          "off": off,
                          "zero field": zero,
                          "x7_sf": x7_sf,
                          "-x7_sf": mx7_sf,
                          "y7_sf": y7_sf,
                          "-y7_sf": my7_sf,
                          "z7_sf": z7_sf,
                          "-z7_sf": mz7_sf,
                          "x7_nsf": x7_nsf,
                          "-x7_nsf": mx7_nsf,
                          "y7_nsf": y7_nsf,
                          "-y7_nsf": my7_nsf,
                          "z7_nsf": z7_nsf,
                          "-z7_nsf": mz7_nsf,
                          "z7_high_sf": z7_high_sf,
                          "z7_high_nsf": z7_high_nsf,
                      },
                      precision = [.1, .1, .1, .1, .1, 0, 0],
                     ),

    flipper_inbeam = device('devices.generic.manual.ManualSwitch',
                            description = 'Is the flipper in the beam?',
                            states = ['in', 'out'],
                           ),

    xyzcoil_inbeam = device('devices.generic.manual.ManualSwitch',
                            description = 'Is the xyz-coil in the beam?',
                            states = ['in', 'out'],
                           ),
)

startupcode = '''
'''
