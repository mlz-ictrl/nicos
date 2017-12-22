# -*- coding: utf-8 -*-

description = 'GALAXI motors'

group = 'optional'

display_order = 7

tango_base = 'tango://localhost:10000/galaxi/'

devices = dict(
    roy = device('nicos_mlz.dns.devices.motor.Motor',
        description = 'ROY axis',
        tangodevice = tango_base + 'fzjs7/ROY',
        offset = 0,
        precision = 0.01,
        userlimits = (-5000, 5000),
    ),
    roz = device('nicos_mlz.dns.devices.motor.Motor',
        description = 'ROZ axis',
        tangodevice = tango_base + 'fzjs7/ROZ',
        offset = 0,
        precision = 0.01,
        userlimits = (-5000, 5000),
    ),
    dofchi = device('nicos_mlz.dns.devices.motor.Motor',
        description = 'DOFChi axis',
        tangodevice = tango_base + 'fzjs7/DOFChi',
        offset = 0,
        precision = 0.01,
        userlimits = (-50, 50),
    ),
    dofom = device('nicos_mlz.dns.devices.motor.Motor',
        description = 'DOFOm axis',
        tangodevice = tango_base + 'fzjs7/DOFOm',
        offset = 0,
        precision = 0.01,
        userlimits = (-50, 50),
    ),
    roby = device('nicos_mlz.dns.devices.motor.Motor',
        description = 'ROBY axis',
        tangodevice = tango_base + 'fzjs7/ROBY',
        offset = 0,
        precision = 0.01,
    ),
    robz = device('nicos_mlz.dns.devices.motor.Motor',
        description = 'ROBZ axis',
        tangodevice = tango_base + 'fzjs7/ROBZ',
        offset = 0,
        precision = 0.01,
    ),
)
