# -*- coding: utf-8 -*-

description = 'setup for tomo with huber rotation stage from antares'

group = 'optional'

tango_base = 'tango://nectarhw.nectar.frm2.tum.de:10000/nectar'

devices = dict(
    sry_huber_mot = device('nicos.devices.entangle.Motor',
        description = 'sry_huber motor for ct',
        tangodevice = tango_base + '/cam/focus',
        abslimits = (-720, 720),
        comtries = 3,
        lowlevel = True,
    ),
    sry_huber    = device('nicos.devices.generic.Axis',
        description = 'sry_huber for ct',
        pollinterval = 5,
        maxage = 12,
        fmtstr = '%.2f',
        userlimits = (-720, 720),
        precision = 0.01,
        motor = 'sry_huber_mot',
    ),
)
