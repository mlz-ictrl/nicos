description = 'ErwiN monochromator devices'

group = 'lowlevel'

devices = dict(
    mtz = device('nicos.devices.generic.VirtualMotor',
        description = 'z translation motor of monochromator system',
        unit = 'mm',
        abslimits = [0, 92],
        speed = 1,
        curvalue = 90,
        visibility = (),
    ),
    mom = device('nicos.devices.generic.VirtualMotor',
        description = 'omega motor of monochromator system',
        unit = 'deg',
        abslimits = [-51.5, -42.5],
        speed = 0.1,
        curvalue = -43,
        visibility = (),
    ),
    mono_select = device('nicos.devices.generic.MultiSwitcher',
        description = 'Mono changer',
        moveables = ['mom', 'mtz'],
        mapping = {
            'Cu': [-45, 2],  # XXX: correct values after neutron checks
            'Ge': [-43, 90],
        },
        fallback = None,
        fmtstr = '%s',
        precision = [0.05, 0.05],
        blockingmove = True,
    ),
    wav = device('nicos.devices.generic.ManualMove',
        description = 'Selected wavelength',
        abslimits = (1, 1.6),
        default = 1.2,
        unit = 'A',
    ),
)
