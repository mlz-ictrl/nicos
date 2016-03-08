# -*- coding: utf-8 -*-

description = "Mini-kappa axes setup"
group = "lowlevel"

tango_base = "tango://phys.biodiff.frm2:10000/biodiff/"

devices = dict(
    minikappa_kappa = device("devices.tango.Motor",
                             description = "Mini-kappa kappa axis",
                             tangodevice = tango_base + "fzjs7/kappa_mini",
                             unit = "deg",
                             precision = 0.01,
                            ),
    minikappa_phi   = device("devices.tango.Motor",
                             description = "Mini-kappa phi axis",
                             tangodevice = tango_base + "fzjs7/phi_mini",
                             unit = "deg",
                             precision = 0.01,
                            ),
    minikappa_omega = device("devices.tango.Motor",
                             description = "Mini-kappa omega axis",
                             tangodevice = tango_base + "fzjs7/omega_mini_stepper",
                             unit = "deg",
                             precision = 0.01,
                             abslimits = (-390, 390),
                            ),
    minikappa_omega_m = device("biodiff.motor.MicrostepMotor",
                               description = "Mini-kappa omega axis "
                                             "(micro)",
                               motor = "minikappa_omega",
                               precision = 0.001,
                               abslimits = (-390, 390),
                              ),
)
