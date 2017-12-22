# -*- coding: utf-8 -*-

description = 'Mini-kappa axes setup'
group = 'lowlevel'

tango_base = 'tango://phys.biodiff.frm2:10000/biodiff/'

devices = dict(
    kappa_minikappa = device('nicos.devices.tango.Motor',
        description = 'Mini-kappa kappa axis',
        tangodevice = tango_base + 'fzjs7/kappa_mini',
        unit = 'deg',
        precision = 0.01,
    ),
    phi_minikappa = device('nicos.devices.tango.Motor',
        description = 'Mini-kappa phi axis',
        tangodevice = tango_base + 'fzjs7/phi_mini',
        unit = 'deg',
        precision = 0.01,
    ),
    omega_minikappa = device('nicos.devices.tango.Motor',
        description = 'Mini-kappa omega axis',
        tangodevice = tango_base + 'fzjs7/omega_mini_stepper',
        unit = 'deg',
        precision = 0.01,
        abslimits = (-390, 390),
    ),
    omega_minikappa_m = device('nicos_mlz.biodiff.devices.motor.MicrostepMotor',
        description = 'Mini-kappa omega axis (micro)',
        motor = 'omega_minikappa',
        precision = 0.001,
        abslimits = (-390, 390),
    ),
    omega_minikappa_cod = device('nicos.devices.tango.Sensor',
        description = 'Mini-kappa omega encoder (23 bit)',
        tangodevice = tango_base + 'FZJDP_Analog/omega_mini_stepper',
        fmtstr = '%.3f',
        unit = 'deg',
    ),
)
