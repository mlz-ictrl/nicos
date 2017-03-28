# -*- coding: utf-8 -*-

description = 'WMI microwave generator'

group = 'optional'

includes = []

tango_base = 'tango://%s:10000/box/' % setupname

devices = dict(
    modulation_io = device('devices.tango.DigitalOutput',
        description = 'Tango device for the modulation switch',
        tangodevice = tango_base + 'rfgen/modulation',
        lowlevel = True,
    ),
    swmodulation = device('devices.generic.Switcher',
        description = 'Modulation switch',
        moveable = 'modulation_io',
        mapping = {'on': 1,
                   'off': 0},
        fallback = '<undefined>',
        precision = 0,
    ),
    output_io = device('devices.tango.DigitalOutput',
        description = 'Tango device for the output switch',
        tangodevice = tango_base + 'rfgen/output',
        lowlevel = True,
    ),
    swoutput = device('devices.generic.Switcher',
        description = 'Output switch',
        moveable = 'output_io',
        mapping = {'on': 1,
                   'off': 0},
        fallback = '<undefined>',
        precision = 0,
    ),
    frequency = device('sans1.wmirfgen.Frequency',
        description = 'Device the frequency and frequency modulation',
        tangodevice = tango_base + 'rfgen/frequency',
        abslimits = (0.1, 40000)
    ),
    frequency_rf1 = device('devices.tango.AnalogOutput',
        description = 'Tango device for the first '
        'internal frequency generator '
        '(for modulation)',
        tangodevice = tango_base + 'rfgen/mod_rf1',
        abslimits = (0.0, 40000)
    ),
    power = device('devices.tango.AnalogOutput',
        description = 'Tango device for the power level',
        tangodevice = tango_base + 'rfgen/power',
        abslimits = (-130, 30)
    ),
    lockin_x = device('devices.tango.AnalogInput',
        description = 'Lockin x',
        tangodevice = tango_base + 'lockin/x',
        lowlevel = False,
        fmtstr = '%g',
    ),
    lockin_y = device('devices.tango.AnalogInput',
        description = 'Lockin y',
        tangodevice = tango_base + 'lockin/y',
        lowlevel = False,
        fmtstr = '%g',
    ),
    #lockin_vi = device('devices.tango.ReadableChannel',
    #    description = 'Measurable tango device for x/y, measured by the lockin',
    #    tangodevice = tango_base + 'lockin/xy',
    #    valuenames = ['x', 'y'],
    #    lowlevel = True,
    #),
    #lockin = device('devices.generic.Detector',
    #    description = 'Lockin x/y',
    #    others = ['lockin_vi'],
    #    maxage = 8,
    #    pollinterval = 3,
    #),
)
