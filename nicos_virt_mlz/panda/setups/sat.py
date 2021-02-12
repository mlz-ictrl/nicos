#  -*- coding: utf-8 -*-

description = 'setup for sample attenuator'

group = 'optional'

devices = dict(
    sat_inout = device('nicos_virt_mlz.panda.devices.stubs.SatBoxInOut',
        lowlevel = True,
        unit = '',
    ),
    sat = device('nicos_mlz.panda.devices.satbox.SatBox',
        description = 'Sample beam attenuator',
        input = 'sat_inout',
        output = 'sat_inout',
        unit = 'mm',
        fmtstr = '%d',
        blades = [1, 2, 5, 10, 20],
        # blades = [0, 2, 5, 10, 20],  # code for nonworking blade
        readout = 'outputs',
    ),
)
