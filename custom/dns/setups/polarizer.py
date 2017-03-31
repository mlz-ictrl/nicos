# -*- coding: utf-8 -*-

description = 'DNS polarizer'
group = 'lowlevel'

tango_base = 'tango://phys.dns.frm2:10000/dns/'

# first value is translation, second is rotation
POLARIZER_POSITIONS = {
    'in':  [2.4, 6],
    # XXX: need the current values for this
    'out': [0, 0],
}

devices = dict(
    # pol_inbeam   = device('devices.generic.MultiSwitcher',
    #                       description = 'Automatic in/out switch for the polarizer',
    #                       mapping = POLARIZER_POSITIONS,
    #                       fallback = 'unknown',
    #                       moveables = ['pol_trans', 'pol_rot'],
    #                       precision = [0.1, 0.1],
    #                      ),
    pol_inbeam   = device('devices.generic.ManualSwitch',
                          description = 'In/out switch for the polarizer',
                          states = ['in', 'out'],
                         ),

    pol_trans    = device('devices.tango.Motor',
                          description = 'Polarizer translation',
                          tangodevice = tango_base + 'fzjs7/pol_trans',
                         ),
    pol_rot      = device('devices.tango.Motor',
                          description = 'Polarizer rotation',
                          tangodevice = tango_base + 'fzjs7/pol_rot',
                         ),
)
