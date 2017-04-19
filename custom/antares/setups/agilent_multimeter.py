# -*- coding: utf-8 -*-

description = 'Agilent multimeter'

group = 'optional'

includes = []

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    R_agilent_multimeter = device('devices.tango.Sensor',
        description = 'Agilent multimeter: 4-wire resistance',
        tangodevice = tango_base + 'agilent_multimeter/fresistance',
    ),
)
