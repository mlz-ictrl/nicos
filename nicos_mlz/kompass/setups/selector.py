description = 'Selector related devices'

group = 'lowlevel'

nethost = 'kompasshw.kompass.frm2'

devices = dict(
    nvslift_m = device('nicos.devices.taco.Motor',
        description = 'Neutron selector lift motor',
        tacodevice = '//%s/kompass/lift/motor' % nethost,
        abslimits = (0, 406.5),
        unit = 'mm',
        lowlevel = True,
    ),
    nvslift = device('nicos.devices.generic.Switcher',
        description = 'Neutron selector lift',
        moveable = 'nvslift_m',
        mapping = {'out': 0.,
                   'in': 406.01},
        fallback = '',
        fmtstr = '%s',
        precision = 0.1,
        blockingmove = False,
        lowlevel = False,
        unit = '',
    ),
)
