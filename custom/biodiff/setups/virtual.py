# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"
__date__    = "2014-05-05"
__version__ = "0.1.0"


description = "Test setup for virtual devices"
group = "optional"

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
               )
