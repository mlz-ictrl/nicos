description = 'Selector related devices'

group = 'lowlevel'

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/'

devices = dict(
    nvslift_m = device('nicos.devices.tango.Motor',
        description = 'Neutron selector lift motor',
        tangodevice = tango_base + 'lift/motor',
        unit = 'mm',
        lowlevel = True,
    ),
    nvslift_c = device('nicos.devices.tango.Sensor',
        description = 'Selector lift coder',
        tangodevice = tango_base + 'lift/coder',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    nvslift_ax = device('nicos.devices.generic.Axis',
        description = 'Selector lift position',
        motor = 'nvslift_m',
#        coder = 'nvslift_c',  # temporarily, as the coder seems broken
        coder = 'nvslift_m',
        fmtstr = '%.2f',
        precision = 0.1,
    ),
    nvslift = device('nicos.devices.generic.Switcher',
        description = 'Neutron selector lift',
        moveable = 'nvslift_ax',
        mapping = {'out': 0.,
                   'in': 405.377},
        fallback = '',
        fmtstr = '%s',
        precision = 1.0,
        blockingmove = False,
        lowlevel = False,
        unit = '',
    ),
)
