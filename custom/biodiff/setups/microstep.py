# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"
__date__    = "2014-05-08"
__version__ = "0.1.0"


description = "Software based micro stepping for several axes"
group = "optional"

includes = ["motor"]

devices = dict(
        omega_samplestepper_m = device("biodiff.motor.MicrostepMotor",
                                       description = "Sample stepper " +
                                       "omega variant (micro)",
                                       motor = "omega_samplestepper",
                                       ),
        omega_sampletable_m = device("biodiff.motor.MicrostepMotor",
                                     description = "Sample table " +
                                     "omega variant (micro)",
                                     motor = "omega_sampletable",
                                     ),
               )
