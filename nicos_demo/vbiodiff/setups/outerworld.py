# -*- coding: utf-8 -*-

description = "Outside world data"
group = "lowlevel"

devices = dict(
    ubahn = device('nicos_mlz.devices.ubahn.UBahn',
        description = 'Next subway departures',
    ),
    meteo = device('nicos.devices.generic.VirtualCoder',
        description = 'Outdoor air temperature',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-30, 40),
            curvalue = 20,
            ramp = 0.1,
            unit = 'degC',
        ),
    ),
)
