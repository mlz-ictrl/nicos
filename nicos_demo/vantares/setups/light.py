# -*- coding: utf-8 -*-
description = 'light in ANTARES bunker'

group = 'lowlevel'

devices = dict(
    light = device('nicos.devices.generic.ManualSwitch',
        description = 'light in ANTARES bunker',
        states = ['on', 'off'],
    ),
)
