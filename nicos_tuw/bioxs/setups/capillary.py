description = 'Capillary Optics'
group = 'lowlevel'

tango_base_motor = 'tango://bioxs:10000/motor/'

devices = dict(
    # x-axis
    tcx_m = device('nicos.devices.entangle.Motor',
        description = 'Capillary translation x-Axis motor',
        tangodevice = tango_base_motor + 'NewFocus/tcx_motor',
        visibility = (),
    ),
    tcx = device('nicos.devices.generic.Axis',
        description = 'Capillary translation x-Axis motor',
        motor = 'tcx_m',
        precision = 0.001,
    ),
    # y-axis
    tcy_m = device('nicos.devices.entangle.Motor',
        description = 'Capillary translation y-Axis motor',
        tangodevice = tango_base_motor + 'NewFocus/tcy_motor',
        visibility = (),
    ),
    tcy = device('nicos.devices.generic.Axis',
        description = 'Capillary translation y-Axis motor',
        motor = 'tcy_m',
        precision = 0.001,
    ),
    # z-axis
    tcz_m = device('nicos.devices.entangle.Motor',
        description = 'Capillary translation y-Axis motor',
        tangodevice = tango_base_motor + 'NewFocus/tcz_motor',
        visibility = (),
    ),
    tcz = device('nicos.devices.generic.Axis',
        description = 'Capillary translation z-Axis motor',
        motor = 'tcz_m',
        precision = 0.001,
    ),
    # tip
    gcx_m = device('nicos.devices.entangle.Motor',
        description = 'Capillary Tip motor',
        tangodevice = tango_base_motor + 'NewFocus/gcx_motor',
        visibility = (),
    ),
    gcx = device('nicos.devices.generic.Axis',
        description = 'Capillary Tip motor',
        motor = 'gcx_m',
        precision = 0.001,
    ),
    # tilt
    gcy_m = device('nicos.devices.entangle.Motor',
        description = 'Capillary Tilt motor',
        tangodevice = tango_base_motor + 'NewFocus/gcy_motor',
        visibility = (),
    ),
    gcy = device('nicos.devices.generic.Axis',
        description = 'Capillary Tilt motor',
        motor = 'gcy_m',
        precision = 0.001,
    ),
)

startupcode = '''
SetDetectors(det_eiger)
'''
