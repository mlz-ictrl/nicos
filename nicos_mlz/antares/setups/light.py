# -*- coding: utf-8 -*-
description = 'light in ANTARES bunker'

group = 'optional'

includes = []

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    light = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'light in ANTARES bunker',
        tangodevice = tango_base + 'fzjdp_digital/LichtBunker',
        mapping = dict(
            on = 1, off = 0
        ),
    ),
)
