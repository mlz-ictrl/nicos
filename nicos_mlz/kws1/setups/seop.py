# -*- coding: utf-8 -*-

description = "SEOP polarizer"
group = "optional"

devices = dict(
    seop_flip = device("nicos_mlz.maria.devices.pyro4.DigitalOutput",
        description = "Pyro4 Device",
        pyro4device = "PYRO:he3.cell@seopsrv.kws1.frm2:50555",
        hmackey = "iamverysecret",
    ),
)
