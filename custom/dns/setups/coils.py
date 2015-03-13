# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"


description = "Coil setup"
group = "optional"

tango_host = 'tango://phys.dns.frm2:10000'
_GPIB_URL = tango_host + '/dns/gpib/%d'
_DIO_URL = tango_host + '/dns/FZJDP_Digital/%s'
_POLCHANGE = {"+": 0, "-": 1}

##
# magnetic field definitions on 13-03-2015
off     = (0, 0, 0, 0, 0, (0, 0), "off")
zero    = (0, .15, -.50, -2.15, -2.15, (.97, .56), "on")
# fields with spin flipper
x7_sf   = (0, -2.0, -.70, -2.15, -2.15, (0.95,0.42), "on")
mx7_sf  = (0, 2.30, -0.35, -2.15, -2.15, (1.05, 0.38), "on")
y7_sf   = (0, 1.70, -2.65, -2.15, -2.15, (0.90,0.42), "on")
my7_sf  = (0, -1.40, 1.65, -2.15, -2.15, (0.98, 0.38), "on")
z7_sf   = (0, .15, -.50, 0.0, 0.0, (0.98,0.30), "on")
mz7_sf  = (0, .15, -.50, -4.30, -4.30, (1.20, 0.20), "on")
# fields without spin flipper
x7_nsf  = x7_sf[:6] + ("off", )
mx7_nsf = mx7_sf[:6] + ("off", )
y7_nsf  = y7_sf[:6] + ("off", )
my7_nsf = my7_sf[:6] + ("off", )
z7_nsf  = z7_sf[:6] + ("off", )
mz7_nsf = mz7_sf[:6] + ("off", )


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
                      tangodevice = _DIO_URL % 'Polum2',
                      mapping = _POLCHANGE,
                      lowlevel = True
                     ),
    Fi       = device('dns.toellner.CurrentToellner',
                      description = 'Flipper Field',
                      tangodevice = _GPIB_URL % 21,
                      abslimits = (-3.2,3.2),
                      polchange = 'polch_Fi',
                      channel = 2,
                     ),
    polch_Co = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for Flipper Compensation',
                      tangodevice = _DIO_URL % 'Polum1',
                      mapping = _POLCHANGE,
                      lowlevel = True
                     ),
    Co       = device('dns.toellner.CurrentToellner',
                      description = 'Flipper Compensation Field',
                      tangodevice = _GPIB_URL % 21,
                      abslimits = (-3.2,3.2),
                      polchange = 'polch_Co',
                      channel = 1,
                     ),
    A        = device('dns.toellner.CurrentToellner',
                      description = 'Coil A',
                      tangodevice = _GPIB_URL % 22,
                      abslimits = (-3.2,3.2),
                      polchange = 'polch_A',
                      channel = 1,
                     ),
    polch_A  = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for coil A',
                      tangodevice = _DIO_URL % 'Polum3',
                      mapping = _POLCHANGE,
                      lowlevel = True,
                     ),
    B        = device('dns.toellner.CurrentToellner',
                      description = 'Coil B',
                      tangodevice = _GPIB_URL % 22,
                      abslimits = (-3.2,3.2),
                      polchange = 'polch_B',
                      channel = 2,
                     ),
    polch_B  = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for coil B',
                      tangodevice = _DIO_URL % 'Polum4',
                      mapping = _POLCHANGE,
                      lowlevel = True,
                     ),
    ZB       = device('dns.toellner.CurrentToellner',
                      description = 'Coil-Z Bottom',
                      tangodevice = _GPIB_URL % 23,
                      abslimits = (-5, 5),
                      polchange = 'polch_ZB',
                      channel = 1,
                     ),
    polch_ZB = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for coil Z Bottom',
                      tangodevice = _DIO_URL % 'Polum5',
                      mapping = _POLCHANGE,
                      lowlevel = True,
                     ),
    ZT       = device('dns.toellner.CurrentToellner',
                      description = 'Coil-Z Top',
                      tangodevice = _GPIB_URL % 23,
                      abslimits = (-5, 5),
                      polchange = 'polch_ZT',
                      channel = 2,
                     ),
    polch_ZT = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for coil Z Top',
                      tangodevice = _DIO_URL % 'Polum6',
                      mapping = _POLCHANGE,
                      lowlevel = True,
                     ),
    C        = device('dns.toellner.CurrentToellner',
                      description = 'Coil C',
                      tangodevice = _GPIB_URL % 24,
                      abslimits = (-3.2, 3.2),
                      polchange = 'polch_C',
                      channel = 1,
                     ),
    polch_C  = device('devices.tango.NamedDigitalOutput',
                      description = 'Polarity changer for coil C',
                      tangodevice = _DIO_URL % 'Polum7',
                      mapping = _POLCHANGE,
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
                      },
                      precision = [.1, .1, .1, .1, .1, 0, 0],
                     ),
)

startupcode = '''
Fi.voltage = 24
Co.voltage = 24
A.voltage = 24
B.voltage = 24
ZB.voltage = 32
ZT.voltage = 32
C.voltage = 24
'''
