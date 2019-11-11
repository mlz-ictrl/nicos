# -*- coding: utf-8 -*-

description = 'Beam shutter setup'
group = 'lowlevel'
display_order = 5

excludes = ['virtual_shutter']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'
tango_base_mlz = 'tango://ictrlfs.ictrl.frm2:10000/mlz/'

devices = dict(
    shutter_in = device('nicos.devices.tango.DigitalInput',
        tangodevice = tango_base + 'sps/shutter_read',
        lowlevel = True,
    ),
    shutter_set = device('nicos.devices.tango.DigitalOutput',
        tangodevice = tango_base + 'sps/shutter_write',
        lowlevel = True,
    ),
    shutter = device('nicos_mlz.kws1.devices.shutter.Shutter',
        description = 'shutter control',
        output = 'shutter_set',
        input = 'shutter_in',
        timeout = 300,
    ),
    nl3a_shutter = device('nicos.devices.tango.NamedDigitalInput',
        description = 'NL3a shutter status',
        mapping = {'closed': 0,
                   'open': 1},
        tangodevice = tango_base_mlz + 'shutter/nl3a',
        pollinterval = 60,
        maxage = 120,
    ),
    sixfold_shutter = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Sixfold shutter status',
        mapping = {'closed': 0,
                   'open': 1},
        tangodevice = tango_base_mlz + 'shutter/sixfold',
        pollinterval = 60,
        maxage = 120,
    ),
)

extended = dict(
    representative = 'shutter',
)
