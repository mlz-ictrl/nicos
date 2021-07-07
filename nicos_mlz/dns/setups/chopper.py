# -*- coding: utf-8 -*-

description = 'New DNS chopper'
group = 'optional'

tango_base = 'tango://phys.dns.frm2:10000/dns/chopper/_'

devices = dict(
    chopper_rpm = device('nicos.devices.entangle.AnalogOutput',
        description = 'Chopper speed',
        tangodevice = tango_base + 'drehzahl',
        fmtstr = '%.1f',
    ),
    chopper_current = device('nicos.devices.entangle.AnalogInput',
        description = 'Motor current',
        tangodevice = tango_base + 'motorstrom',
        fmtstr = '%.2f',
        unit = 'A',
    ),
    chopper_temp = device('nicos.devices.entangle.AnalogInput',
        description = 'Motor temperature',
        tangodevice = tango_base + 'motortemperatur',
        fmtstr = '%.1f',
        warnlimits = (0, 60),
    ),
    chopper_vacuum = device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure in chopper housing',
        tangodevice = tango_base + 'vakuumdruck',
        fmtstr = '%.2g',
    ),
    chopper_imbalance = device('nicos.devices.entangle.AnalogInput',
        description = 'Chopper vibration',
        tangodevice = tango_base + 'unwucht',
        fmtstr = '%.4f',
        warnlimits = (-1, 0.0009),
    ),
    chopper_bearing1 = device('nicos.devices.entangle.AnalogInput',
        description = 'Bearing unit condition of bearing 1',
        tangodevice = tango_base + 'lager1kennzahl',
        fmtstr = '%.2f',
        warnlimits = (-1, 4.9),
    ),
    chopper_bearing2 = device('nicos.devices.entangle.AnalogInput',
        description = 'Bearing unit condition of bearing 2',
        tangodevice = tango_base + 'lager2kennzahl',
        fmtstr = '%.2f',
        warnlimits = (-1, 4.9),
    ),
)
