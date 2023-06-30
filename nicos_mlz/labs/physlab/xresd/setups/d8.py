# -*- coding: utf-8 -*-

description = 'D8 x-ray instrument'

group = 'optional'

tango_base = configdata('instrument.values')['tango_base'] + 'box/bruker/'

devices = dict(
    d8_rc = device('nicos.devices.entangle.NamedDigitalOutput',
        tangodevice = tango_base + 'd8_remote',
        description = 'D8 remote control mode'
    ),
    # d8_ldoor = device('nicos.devices.generic.ReadonlyParamDevice',
    #     description = 'Left door status',
    #     device = 'd8',
    #     parameter = 'ldoor',
    #     unit = '',
    #     copy_status = False,
    # ),
    # d8_rdoor = device('nicos.devices.generic.ReadonlyParamDevice',
    #     description = 'Right door status',
    #     device = 'd8',
    #     parameter = 'rdoor',
    #     unit = '',
    #     copy_status = False,
    # ),
    d8 = device('nicos_mlz.labs.physlab.xresd.devices.d8.D8',
        description = 'D8 device ...',
        registers = 'd8_reg',
        unit = '',
    ),
    d8_reg = device('nicos.devices.entangle.VectorInput',
        tangodevice = tango_base + 'd8_registers',
        description = 'D8 registers',
        visibility = (),
    ),
)
