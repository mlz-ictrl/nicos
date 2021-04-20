# -*- coding: utf-8 -*-

description = 'Spodi neutron guide'

group = 'lowlevel'

tango_base = 'tango://nguidectrl.spodi.frm2.tum.de:10000/box/'

devices = dict(
    p1_nguide = device('nicos.devices.entangle.Sensor',
        description = 'Pressure 1',
        tangodevice = tango_base + 'leybold/sensor1',
        fmtstr = '%.2f',
        maxage = 65,
        pollinterval = 30,
    ),
    p2_nguide = device('nicos.devices.entangle.Sensor',
        description = 'Pressure 2',
        tangodevice = tango_base + 'leybold/sensor2',
        fmtstr = '%.2f',
        maxage = 65,
        pollinterval = 30,
    ),
    p3_nguide = device('nicos.devices.entangle.Sensor',
        description = 'Pressure 3',
        tangodevice = tango_base + 'leybold/sensor3',
        fmtstr = '%.2f',
        maxage = 65,
        pollinterval = 30,
    ),
    o2_nguide = device('nicos.devices.entangle.Sensor',
        description = 'O2',
        tangodevice = tango_base + 'greisinger/o2',
        fmtstr = '%.2f',
        maxage = 65,
        pollinterval = 30,
    ),
    o2part_nguide = device('nicos.devices.entangle.Sensor',
        description = 'O2 part',
        tangodevice = tango_base + 'greisinger/o2part',
        fmtstr = '%.2f',
        maxage = 65,
        pollinterval = 30,
    ),
    T_nguide = device('nicos.devices.entangle.Sensor',
        description = 'Temperature',
        tangodevice = tango_base + 'greisinger/temp',
        fmtstr = '%.2f',
        maxage = 65,
        pollinterval = 30,
    ),
)

display_order = 100
startupcode = '''
'''
