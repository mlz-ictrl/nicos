# -*- coding: utf-8 -*-

description = 'Setup for the sample environment.'
group = 'optional'

tangohost = 'phys.spheres.frm2'
tango_sample = 'tango://%s:10000/spheres/sample/' % tangohost

devices = dict(
    c_temperature = device('nicos_mlz.spheres.devices.sample.SEController',
        description = 'Temperaturecontroller',
        tangodevice = tango_sample + 'controller',
        pollinterval = 1,
        maxage = 5,
        precision = 0.1
    ),
    T_sample = device('nicos.devices.tango.TemperatureController',
        description = 'Sample temperature regulation',
        tangodevice = tango_sample + 'samplecontroller',
        pollinterval = 2,
        maxage = 5,
        abslimits = (0, 500),
        precision = 0.1,
        lowlevel = True,
    ),
    T_tube = device('nicos.devices.tango.TemperatureController',
        description = 'Tube temperature regulation',
        tangodevice = tango_sample + 'tubecontroller',
        pollinterval = 2,
        maxage = 5,
        abslimits = (0, 300),
        precision = 0.1,
        lowlevel = True,
    ),
    v_flood = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Valve to flood the sample environment '
        'with exchangegas',
        tangodevice = tango_sample + 'floodvalve',
        mapping = {'closed': 0,
                   'open': 1},
        lowlevel = True,
        pollinterval = 2,
        unit = '',
    ),
    v_vacuum = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Valve to evacuate the sample environment',
        tangodevice = tango_sample + 'vacuumvalve',
        mapping = {'closed': 0,
                   'open': 1},
        lowlevel = True,
        pollinterval = 2,
        unit = ''
    ),
    h_sample = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Heater of the sample',
        tangodevice = tango_sample + 'sampleheater',
        mapping = {'off': 0,
                   'low': 1,
                   'medium': 2,
                   'high': 3},
        lowlevel = True,
        pollinterval = 2,
        unit = ''
    ),
    h_tube = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Heater of the tube',
        tangodevice = tango_sample + 'tubeheater',
        mapping = {'off': 0,
                   'low': 1,
                   'medium': 2,
                   'high': 3},
        lowlevel = True,
        pollinterval = 2,
        unit = ''
    ),
    c_pressure = device('nicos_mlz.spheres.devices.sample.PressureController',
        description = 'Sample temperature controller',
        tangodevice = tango_sample + 'pressure',
        controller = tango_sample + 'controller',
        pollinterval = 2,
        maxage = 5,
        precision = 0.1
    ),
    setpoint = device('nicos.devices.generic.paramdev.ReadonlyParamDevice',
        description = 'Device to display the setpoint parameter of the '
                      'temperature controller',
        device = 'c_temperature',
        parameter = 'setpoint',
        unit = 'K'
    ),
)
