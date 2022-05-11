# -*- coding: utf-8 -*-

description = 'Shutter setup'
group = 'lowlevel'
display_order = 5

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'
tango_base_mlz = 'tango://ictrlfs.ictrl.frm2:10000/mlz/'

_MAP_SHUTTER = {
    'open': 1,
    'closed': 0,
}

devices = dict(
    shutter = device('nicos_mlz.jcns.devices.shutter.Shutter',
        description = 'Experiment shutter',
        tangodevice = tango_base + 's7_io/shutter',
        mapping = _MAP_SHUTTER,
    ),
    nl3a_shutter = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'NL3a shutter status',
        tangodevice = tango_base_mlz + 'shutter/nl3a',
        mapping = _MAP_SHUTTER,
        pollinterval = 60,
        maxage = 120,
    ),
    sixfold_shutter = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Sixfold shutter status',
        tangodevice = tango_base_mlz + 'shutter/sixfold',
        mapping = _MAP_SHUTTER,
        pollinterval = 60,
        maxage = 120,
    ),
)

extended = dict(
    representative = 'shutter',
)
