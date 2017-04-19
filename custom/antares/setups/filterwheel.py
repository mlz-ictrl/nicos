# -*- coding: utf-8 -*-

description = 'ANTARES filter wheel'

group = 'optional'

includes = []

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    # PB-Filter
    pbfilter_io = device('devices.tango.DigitalOutput',
        description = 'Tango device for Pb filter in/out',
        tangodevice = tango_base + 'fzjdp_digital/FilterPb',
        lowlevel = True,
    ),
    pbfilter = device('devices.generic.Switcher',
        description = 'Pb filter in/out',
        moveable = 'pbfilter_io',
        mapping = {'in': 1,
                   'out': 2},
        fallback = '<undefined>',
        precision = 0,
    ),

    # Filter Wheel
    filterwheel_inout_io = device('devices.tango.DigitalOutput',
        description = 'Tango device for filter wheel in/out',
        tangodevice = tango_base + 'fzjdp_digital/FilterWheel',
        lowlevel = True,
    ),
    filterwheel_inout = device('devices.generic.Switcher',
        description = 'Filter Wheel in/out',
        moveable = 'filterwheel_inout_io',
        mapping = {'in': 1,
                   'out': 2},
        fallback = '<undefined>',
        precision = 0,
        lowlevel = True,
    ),
    filterwheel_mot = device('devices.tango.Motor',
        tangodevice = tango_base + 'fzjs7/Filterrad',
        precision = 0.,
        lowlevel = True,
    ),
    filterwheel = device('devices.generic.MultiSwitcher',
        description = 'Filterwheel, moves automatical into the beam, if needed',
        moveables = ['filterwheel_mot', 'filterwheel_inout'],
        mapping = dict(
            bi_mono = [1, 'in'],
            sapphire = [2, 'in'],
            bi_poly = [3, 'in'],
            be = [4, 'in'],
            out = [2, 'out']
        ),
        precision = [0, 0],
        blockingmove = True,
    ),
)
