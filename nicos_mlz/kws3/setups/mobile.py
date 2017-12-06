# -*- coding: utf-8 -*-

description = 'Mobile Sample devices'
group = 'optional'
display_order = 40

excludes = ['virtual_sample']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = dict(
    sam_rot = device('nicos.devices.tango.Motor',
        description = 'rot-table inside vacuum chamber 10m',
        tangodevice = tango_base + 'fzjs7/sam_rot',
        unit = 'deg',
        precision = 0.01,
    ),
    sam_phi = device('nicos.devices.tango.Motor',
        description = 'tilt-table-phi in vacuum chamber 10m',
        tangodevice = tango_base + 'fzjs7/sam_phi',
        unit = 'deg',
        precision = 0.01,
    ),
    sam_chi = device('nicos.devices.tango.Motor',
        description = 'tilt-table-chi in vacuum chamber 10m',
        tangodevice = tango_base + 'fzjs7/sam_chi',
        unit = 'deg',
        precision = 0.01,
    ),
)
