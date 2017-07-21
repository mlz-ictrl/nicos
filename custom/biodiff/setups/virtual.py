# -*- coding: utf-8 -*-

description = "Test setup for virtual devices"
group = "optional"

excludes = ['shutter']

devices = dict(
    vmotor = device("nicos.devices.generic.VirtualMotor",
                    description = "Test motor",
                    abslimits = (0, 359),
                    unit = "deg",
                    speed = 1,
                   ),
    micro_motor =  device("nicos_mlz.biodiff.devices.motor.MicrostepMotor",
                          description = "Test device",
                          motor = "vmotor",
                         ),
    gammashutter = device("nicos.devices.generic.ManualSwitch",
                          description = "Gamma shutter (virtual)",
                          states = ["open", "closed"],
                         ),
    photoshutter = device("nicos.devices.generic.ManualSwitch",
                          description = "Photo shutter (virtual)",
                          states = ["open", "closed"],
                         ),
)
