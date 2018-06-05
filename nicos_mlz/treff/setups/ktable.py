# -*- coding: utf-8 -*-
description = 'Axes in detector test table'

group = 'optional'

tango_base = 'tango://phys.treff.frm2:10000/treff/'

devices = dict(
    det_ax = device('nicos.devices.tango.Motor',
                    description = 'X axis',
                    tangodevice = tango_base + 'phytron/ax'),
    det_ay = device('nicos.devices.tango.Motor',
                    description = 'Y axis',
                    tangodevice = tango_base + 'phytron/ay'),
)
