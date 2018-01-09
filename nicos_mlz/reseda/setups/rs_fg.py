# -*- coding: utf-8 -*-

description = 'R&S signal generator from NREX'

group = 'optional'

includes = []

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda/rs_fg/'

devices = dict(
    rs_fg_freq = device('nicos.devices.tango.AnalogOutput',
        description = 'R&S fg frequency',
        tangodevice = tango_base + 'frequency',
    ),
    rs_fg_amp = device('nicos.devices.tango.AnalogOutput',
        description = 'R&S fg amplitude',
        tangodevice = tango_base + 'amplitude',
    ),
    rs_fg_onoff = device('nicos.devices.tango.OnOffSwitch',
        description = 'R&S fg output on/off switch',
        tangodevice = tango_base + 'frequency',
    ),
)
