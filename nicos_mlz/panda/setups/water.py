#  -*- coding: utf-8 -*-

description = 'setup for water flow'

includes = []

group = 'optional'

tango_base = 'tango://phys.panda.frm2:10000/panda/'

devices = dict(
    water = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Water flux readout',
        tangodevice = tango_base + 'water/flow',
        fmtstr = '%s',
        mapping = {'off': 0,
                   'on': 1},
    ),
)
