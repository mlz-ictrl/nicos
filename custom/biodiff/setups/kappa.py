# -*- coding: utf-8 -*-

description = "Mini-kappa axes setup"
group = "lowlevel"

tango_host = "tango://phys.biodiff.frm2:10000"
_TANGO_URL = tango_host + "/biodiff/FZJS7/"

devices = dict(
    minikappa_kappa = device("devices.tango.Motor",
                             description = "Mini-kappa kappa axis",
                             tangodevice = _TANGO_URL + "kappa_mini",
                             unit = "deg",
                             precision = 0.01,
                            ),
    minikappa_phi   = device("devices.tango.Motor",
                             description = "Mini-kappa phi axis",
                             tangodevice = _TANGO_URL + "phi_mini",
                             unit = "deg",
                             precision = 0.01,
                            ),
    minikappa_omega = device("devices.tango.Motor",
                             description = "Mini-kappa omega axis",
                             tangodevice = _TANGO_URL + "omega_mini_stepper",
                             unit = "deg",
                             precision = 0.01,
                            ),
)
