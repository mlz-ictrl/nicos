# -*- coding: utf-8 -*-

description = "Software based micro stepping for several axes"
group = "lowlevel"

includes = ["motor"]

devices = dict(
    omega_samplestepper_m = device("nicos_mlz.biodiff.devices.motor.MicrostepMotor",
                                   description = "Sample stepper omega variant"
                                                 " (micro)",
                                   motor = "omega_samplestepper",
                                   precision = 0.001,
                                  ),
    omega_sampletable_m = device("nicos_mlz.biodiff.devices.motor.MicrostepMotor",
                                 description = "Sample table omega variant "
                                               "(micro)",
                                 motor = "omega_sampletable",
                                 precision = 0.001,
                                ),
)
