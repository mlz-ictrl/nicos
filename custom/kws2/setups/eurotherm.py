# -*- coding: utf-8 -*-

description = 'setup for Eurotherm sample heater'
group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    T_et = device('devices.tango.TemperatureController',
                  description = 'Eurotherm temperature controller',
                  tangodevice = tango_base + 'eurotherm/control',
                  abslimits = (0, 200),
                  precision = 0.1,
                 ),
)

alias_config = dict(T={'T_et': 100})
