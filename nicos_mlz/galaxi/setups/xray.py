# -*- coding: utf-8 -*-

description = 'GALAXI x-ray beam alignment motors'

group = 'optional'

display_order = 7

tango_base = 'tango://phys.galaxi.kfa-juelich.de:10000/galaxi/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    roy = device('nicos_mlz.jcns.devices.motor.Motor',
        description = 'ROY axis',
        tangodevice = s7_motor + 'roy',
        offset = 0,
        precision = 0.01,
        fmtstr = '%d',
        userlimits = (-5000, 5000),
    ),
    roz = device('nicos_mlz.jcns.devices.motor.Motor',
        description = 'ROZ axis',
        tangodevice = s7_motor + 'roz',
        offset = 0,
        precision = 0.01,
        fmtstr = '%d',
        userlimits = (-5000, 5000),
    ),
    dofchi = device('nicos_mlz.jcns.devices.motor.Motor',
        description = 'DOFChi axis',
        tangodevice = s7_motor + 'dofchi',
        offset = 0,
        precision = 0.01,
        userlimits = (-50, 50),
    ),
    dofom = device('nicos_mlz.jcns.devices.motor.Motor',
        description = 'DOFOm axis',
        tangodevice = s7_motor + 'dofom',
        offset = 0,
        precision = 0.01,
        userlimits = (-50, 50),
    ),
    roby = device('nicos_mlz.jcns.devices.motor.Motor',
        description = 'ROBY axis',
        tangodevice = s7_motor + 'roby',
        offset = 0,
        precision = 0.01,
    ),
    robz = device('nicos_mlz.jcns.devices.motor.Motor',
        description = 'ROBZ axis',
        tangodevice = s7_motor + 'robz',
        offset = 0,
        precision = 0.01,
    ),
)
