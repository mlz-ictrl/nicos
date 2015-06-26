# -*- coding: utf-8 -*-

description = "Test setup for virtual devices"
group = "optional"

excludes = ['shutter']

devices = dict(
    vmotor = device("devices.generic.VirtualMotor",
                    description = "Test motor",
                    abslimits = (0, 359),
                    unit = "deg",
                    speed = 1,
                   ),
    micro_motor =  device("biodiff.motor.MicrostepMotor",
                          description = "Test device",
                          motor = "vmotor",
                         ),
    gammashutter = device("devices.generic.ManualSwitch",
                          description = "Gamma shutter (virtual)",
                          states = ["open", "closed"],
                         ),
    photoshutter = device("devices.generic.ManualSwitch",
                          description = "Photo shutter (virtual)",
                          states = ["open", "closed"],
                         ),
)
