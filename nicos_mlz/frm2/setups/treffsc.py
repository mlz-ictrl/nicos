#  -*- coding: utf-8 -*-

description = 'samplechanger for the neutron optics group, used @TREFF'
group = 'plugplay'

devices = dict(
    transAxis = device('nicos.devices.tango.Motor',
        tangodevice = 'tango://treffsc:10000/treffsc/thorlabs/motor',
        description = 'translation axis',
        abslimits = (0, 300),
        userlimits = (0, 300),
        speed = 5,
        unit = 'mm',
    ),
)

