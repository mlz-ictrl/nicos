# -*- coding: utf-8 -*-

description = 'Beamstop setup'
group = 'lowlevel'
display_order = 66

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    beamstop = device('nicos_mlz.kws3.devices.resolution.Beamstop',
        description = 'select beamstop presets',
        moveable = 'det_beamstop_x',
        resolution = 'resolution',
        outpos = 100,
    ),
    det_beamstop_x = device('nicos.devices.tango.Motor',
        description = 'beamstop x',
        tangodevice = s7_motor + 'beamstop_x',
        unit = 'mm',
        precision = 0.5,
    ),
)

extended = dict(
    representative = 'beamstop',
    poller_cache_reader = ['resolution'],
)
