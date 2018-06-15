# -*- coding: utf-8 -*-

description = 'Timer for the spheres detectors'

devices = dict(
    timer = device('nicos.devices.generic.virtual.VirtualTimer',
        description = 'Timer channel',
        lowlevel = True
    ),
)
