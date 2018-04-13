# -*- coding: utf-8 -*-

description = 'Polarizer setup'
group = 'lowlevel'
display_order = 60

excludes = ['virtual_polarizer']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    polarizer = device('nicos_mlz.kws2.devices.polarizer.Polarizer',
        description = 'high-level polarizer switcher',
        input_in = 'pol_in',
        input_out = 'pol_out',
        output = 'pol_set',
        flipper = 'flipper',
        timeout = 60,
    ),
    pol_set = device('nicos.devices.tango.DigitalOutput',
        tangodevice = tango_base + 'sps/pol_write',
        fmtstr = '%#x',
        lowlevel = True,
    ),
    pol_in = device('nicos.devices.tango.DigitalInput',
        tangodevice = tango_base + 'sps/pol_in',
        fmtstr = '%#x',
        lowlevel = True,
    ),
    pol_out = device('nicos.devices.tango.DigitalInput',
        tangodevice = tango_base + 'sps/pol_out',
        fmtstr = '%#x',
        lowlevel = True,
    ),
    flipper = device('nicos.devices.generic.ManualSwitch',
        description = '3He spin flipper (currently virtual)',
        states = ['up', 'down'],
    ),
    #flipper = device("nicos_mlz.maria.devices.pyro4.NamedDigitalOutput",
    #    description = "Pyro4 Device",
    #    pyro4device = "PYRO:he3.cell@3he.kws2.frm2:50555",
    #    hmackey = "iamverysecret",
    #    mapping = {
    #        "down": 0,
    #        "up": 1,
    #    }
    #),
)
