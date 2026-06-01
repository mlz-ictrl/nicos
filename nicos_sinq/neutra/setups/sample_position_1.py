# Sample position 1 only have dynamically allocated motors
description = 'Sample position 1 motorization'

group = 'lowlevel'

display_order = 30

devices = dict(
    sp1_mm = device('nicos_sinq.devices.epics.dynamic.MasterMacsNode',
                    pvprefix = 'NEUTRA:MMSP1',
                    pvsuffixes = configdata('config.dynamic_motor_suffixes'),
                    visibility = {'metadata', 'namespace'},
    )
)
