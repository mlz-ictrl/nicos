# -*- coding: utf-8 -*-

description = 'ANTARES filter wheel'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    # PB-Filter
    pbfilter_io = device('nicos.devices.entangle.DigitalOutput',
        description = 'Tango device for Pb filter in/out',
        tangodevice = tango_base + 'fzjdp_digital/FilterPb',
        visibility = (),
    ),
    pbfilter = device('nicos.devices.generic.Switcher',
        description = 'Pb filter in/out',
        moveable = 'pbfilter_io',
        mapping = {'in': 1,
                   'out': 2},
        fallback = '<undefined>',
        precision = 0,
    ),

    # Filter Wheel
    filterwheel_inout_io = device('nicos.devices.entangle.DigitalOutput',
        description = 'Tango device for filter wheel in/out',
        tangodevice = tango_base + 'fzjdp_digital/FilterWheel',
        visibility = (),
    ),
    filterwheel_inout = device('nicos.devices.generic.Switcher',
        description = 'Filter Wheel in/out',
        moveable = 'filterwheel_inout_io',
        mapping = {'in': 1,
                   'out': 2},
        fallback = '<undefined>',
        precision = 0,
        visibility = (),
    ),
    filterwheel_mot = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'fzjs7/Filterrad',
        precision = 0.,
        visibility = (),
    ),
    filterwheel = device('nicos.devices.generic.MultiSwitcher',
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

monitor_blocks = dict(
    default = Block('Filterwheel',
        [
            BlockRow(
                Field(dev='filterwheel', width=14),
                Field(dev='pbfilter', width=14),
            ),
        ],
        setups=setupname,
    ),
)
